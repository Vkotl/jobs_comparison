from datetime import date

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from helpers import print_difference, delete_positions_date
from compare_positions import get_company_jobs, crosscheck_jobs


def _handle_positions_dict(file_name, pos_dict):
    with open(file_name, encoding='utf8') as f:
        lines = f.read().splitlines()
    lines.pop(0)
    department = ''
    while len(lines) > 0:
        line = lines.pop(0)
        if line.startswith('@'):
            department = line[1:]
            pos_dict[department] = []
        else:
            pos_dict[department].append(line)
    return pos_dict


def compare_galileo(old_date: date, new_date: date):
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, 'Galileo')
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'Galileo changes between {old_date:%Y.%m.%d} and '
          f'{new_date:%Y.%m.%d}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])


def _handle_department(department: WebElement) -> tuple[str, list]:
    dept_name = _find_elem_class(
        department, 'DepartmentSection__Title-sc-1gi5hyp-2').text
    positions = _find_elems_class(department, 'Opening__Wrapper-sc-1ghm7ee-0')
    position_results = []
    for position in positions:
        name = position.find_element(
            By.TAG_NAME, value='a').get_attribute('innerHTML')
        location = position.find_element(
            By.TAG_NAME, value='div').get_attribute('innerHTML')
        position_results.append(f'{name} ({location})')
    return dept_name, position_results


def scrape_galileo():
    url = 'https://www.galileo-ft.com/careers/'
    driver = webdriver.Firefox()
    driver.implicitly_wait(time_to_wait=20)
    driver.get(url)
    try:
        departments = _find_elems_class(driver, 'DepartmentSection__Wrapper-sc-1gi5hyp-0')
        conn = sqlite3.connect('sofijobs.db')
        cursor = conn.cursor()
        _create_company_if_not_exists(conn, cursor)
        position_date = date.today()
        delete_positions_date(cursor, position_date, 'Galileo')
        for department in departments:
            department_data = _handle_department(department)
            department_id = _create_department_if_not_exists_get(
                cursor, department_data[0])
            for position in department_data[1]:
                _create_position(
                    cursor, department_id, position_date, position)
        conn.commit()
        conn.close()
    except TimeoutException:
        print('Failed')
    driver.close()


def _find_elems_class(objects, class_name):
    return objects.find_elements(By.CLASS_NAME, value=class_name)


def _find_elem_class(objects, class_name):
    return objects.find_element(By.CLASS_NAME, value=class_name)


def _create_position(cursor, department_id, jobdate, position):
    cursor.execute(
        'INSERT INTO position VALUES '
        f'("{position}", "{jobdate:%Y-%m-%d}", {department_id});')


def _create_department_if_not_exists_get(cursor, department: str) -> int:
    cursor.execute('SELECT rowid FROM department '
                   f'WHERE company="Galileo" AND name="{department}";')
    if (department_id := cursor.fetchone()) is None:
        cursor.execute('INSERT INTO department VALUES '
                       f'("{department}", "Galileo");')
        cursor.execute('SELECT rowid FROM department '
                       f'WHERE company="Galileo" AND name="{department}";')
        department_id = cursor.fetchone()
    return department_id[0]


def _create_company_if_not_exists(conn, cursor):
    cursor.execute('SELECT name FROM company WHERE name="Galileo";')
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO company VALUES ("Galileo");')
        conn.commit()


def main():
    scrape_galileo()
    # compare_galileo()


if __name__ == '__main__':
    main()
