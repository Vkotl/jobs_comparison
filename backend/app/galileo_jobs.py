"""Handle scraping and writing to database the Galileo positions."""
import pytz
from datetime import date, datetime

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from .constants import GALILEO_CAREERS_URL
from .types import Company, Department, Position
from .helpers import delete_positions_date, build_db_path
from .compare_positions import (
    get_company_jobs, crosscheck_jobs, print_difference)


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
    """Compare and print the positions differences between two dates."""
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, 'Galileo')
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'Galileo changes between {old_date:%Y.%m.%d} and '
          f'{new_date:%Y.%m.%d}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])


def _handle_department(
        department: WebElement, company: Company, pos_date: date
        ) -> list[Position]:
    dept_name = _find_elem_class(
        department, 'DepartmentSection__Title-sc-1gi5hyp-2').text
    dept_obj = Department(name=dept_name, company=company)
    positions = _find_elems_class(department, 'Opening__Wrapper-sc-1ghm7ee-0')
    position_results = []
    for position in positions:
        name = position.find_element(
            By.TAG_NAME, value='a').get_attribute('innerHTML').strip()
        if 'amp;' in name:
            name = name.replace('amp;', '').strip()
        location = position.find_element(
            By.TAG_NAME, value='div').get_attribute('innerHTML').strip()
        if 'amp;' in location:
            location = location.replace('amp;', '').strip()
        position_results.append(
            Position(name=name, location=location, department=dept_obj,
                     date=pos_date))
    return position_results


def scrape_galileo():
    """Scrape the Galileo positions from the site."""
    driver = webdriver.Firefox()
    driver.implicitly_wait(time_to_wait=20)
    driver.get(GALILEO_CAREERS_URL)
    try:
        departments = _find_elems_class(
            driver, 'DepartmentSection__Wrapper-sc-1gi5hyp-0')
        conn = sqlite3.connect(build_db_path())
        company = Company(name='Galileo')
        cursor = conn.cursor()
        _create_company_if_not_exists(conn, cursor, company)
        position_date = datetime.now(pytz.timezone('US/Eastern')).date()
        delete_positions_date(cursor, position_date, company)
        for department in departments:
            position_data = _handle_department(
                department, company, position_date)
            department_id = _create_department_get(
                cursor, position_data[0].department)
            for position in position_data:
                _create_position(cursor, department_id, position)
        conn.commit()
        conn.close()
    except TimeoutException:
        print('Failed')
    driver.close()


def _find_elems_class(objects, class_name):
    return objects.find_elements(By.CLASS_NAME, value=class_name)


def _find_elem_class(objects, class_name):
    return objects.find_element(By.CLASS_NAME, value=class_name)


def _create_position(cursor, department_id, position: Position):
    cursor.execute(
        'INSERT INTO position VALUES '
        f'("{position.name} ({position.location})", "{position.date:%Y-%m-%d}"'
        f', {department_id});')


def _create_department_get(cursor, department: Department) -> int:
    """
        Create a department if it doesn't already exist and return id.

    :param cursor: Database cursor.
    :param department: The department typing object to create in the database.
    :return: The id of the department in the database.
    """
    company_name = department.company.name
    cursor.execute('SELECT rowid FROM department '
                   f'WHERE company="{company_name}" '
                   f'AND name="{department.name}";')
    if (department_id := cursor.fetchone()) is None:
        cursor.execute('INSERT INTO department VALUES '
                       f'("{department.name}", "{company_name}");')
        cursor.execute('SELECT rowid FROM department '
                       f'WHERE company="{company_name}" '
                       f'AND name="{department.name}";')
        department_id = cursor.fetchone()
    return department_id[0]


def _create_company_if_not_exists(conn, cursor, company: Company):
    cursor.execute(f'SELECT name FROM company WHERE name="{company.name}";')
    if cursor.fetchone() is None:
        cursor.execute(f'INSERT INTO company VALUES ("{company.name}");')
        conn.commit()


def _main():
    scrape_galileo()
    # compare_galileo()


if __name__ == '__main__':
    _main()
