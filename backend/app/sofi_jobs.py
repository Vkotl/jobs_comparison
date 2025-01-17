"""Handle scraping and writing to database the SoFi positions."""
import pytz
from datetime import date, datetime

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from .constants import SOFI_CAREERS_URL
from .helpers import delete_positions_date, build_db_path
from .compare_positions import (
    crosscheck_jobs, get_company_jobs, print_difference)


def sofi_jobs_check(old_date: date, new_date: date):
    """Compare and print the positions differences between two dates."""
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, 'SoFi')
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'SoFi changes between {old_date:%Y.%m.%d} and {new_date:%Y.%m.%d}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])


def scrape_sofi():
    """Scrape the Galileo positions from the site."""
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; '
                         'x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options)
    driver.implicitly_wait(time_to_wait=40)
    driver.get(SOFI_CAREERS_URL)
    try:
        departments = _find_elems_class(driver, 'dept')
        conn = sqlite3.connect(build_db_path())
        cursor = conn.cursor()
        _create_company_if_not_exists(conn, cursor)
        position_date = datetime.now(pytz.timezone('US/Eastern')).date()
        delete_positions_date(cursor, position_date, 'SoFi')
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


def _create_position(cursor, department_id, jobdate, position):
    cursor.execute(
        'INSERT INTO position VALUES '
        f'("{position}", "{jobdate:%Y-%m-%d}", {department_id});')


def _create_department_if_not_exists_get(cursor, department: str) -> int:
    cursor.execute('SELECT rowid FROM department '
                   f'WHERE company="SoFi" AND name="{department}";')
    if (department_id := cursor.fetchone()) is None:
        cursor.execute('INSERT INTO department VALUES '
                       f'("{department}", "SoFi");')
        cursor.execute('SELECT rowid FROM department '
                       f'WHERE company="SoFi" AND name="{department}";')
        department_id = cursor.fetchone()
    return department_id[0]


def _handle_department(department: WebElement) -> tuple[str, list]:
    dept_name = _find_elem_class(department, 'dept-title').text.strip()
    positions = _find_elems_class(department, 'job')
    position_results = []
    for position in positions:
        name = position.find_element(
            By.CLASS_NAME, value='job-title').get_attribute('innerHTML')
        if 'amp;' in name:
            name = name.replace('amp;', '').strip()
        # location = position.find_element(
        #     By.CLASS_NAME, value='job-location').get_attribute('innerHTML')
        position_results.append(name)
    return dept_name, position_results


def _create_company_if_not_exists(conn, cursor):
    cursor.execute('SELECT name FROM company WHERE name="SoFi";')
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO company VALUES ("SoFi");')
        conn.commit()


def _find_elems_class(objects, class_name):
    return objects.find_elements(By.CLASS_NAME, value=class_name)


def _find_elem_class(objects, class_name):
    return objects.find_element(By.CLASS_NAME, value=class_name)


def _main():
    scrape_sofi()


if __name__ == '__main__':
    _main()
