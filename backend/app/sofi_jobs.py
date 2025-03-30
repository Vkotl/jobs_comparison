"""Handle scraping and writing to database the SoFi positions."""
import pytz
from datetime import date, datetime

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from .proj_typing import Company
from .helpers import delete_positions_date, build_db_path, strip_html_chr
from .constants import (
    SOFI_CAREERS_URL, SOFI_DEPARTMENT_TITLE_CLASS, SOFI_POSITION_WRAPPER_CLASS,
    SOFI_POSITION_TITLE_CLASS, SOFI_DEPARTMENT_WRAPPER_CLASS)


def scrape_sofi():
    """Scrape the Galileo positions from the site."""
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; '
                         'x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options)
    driver.implicitly_wait(time_to_wait=40)
    driver.get(SOFI_CAREERS_URL)
    try:
        departments = _find_elems_class(driver, SOFI_DEPARTMENT_WRAPPER_CLASS)
        conn = sqlite3.connect(build_db_path())
        company = Company(name='SoFi')
        cursor = conn.cursor()
        _create_company_if_not_exists(conn, cursor, company)
        position_date = datetime.now(pytz.timezone('US/Eastern')).date()
        delete_positions_date(cursor, position_date, company)
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


def _create_position(cursor, department_id, jobdate: date, position):
    data = (position[0], jobdate.strftime('%Y-%m-%d'), department_id,
            position[1])
    cursor.execute('INSERT INTO position VALUES (?, ?, ?, ?);', data)


def _create_department_if_not_exists_get(cursor, department: str) -> int:
    db_data = (department,)
    cursor.execute('SELECT rowid FROM department '
                   'WHERE company="SoFi" AND name=?;', db_data) # nosec B608
    if (department_id := cursor.fetchone()) is None:
        cursor.execute('INSERT INTO department VALUES (?, "SoFi");',
                       db_data) # nosec B608
        cursor.execute(
            'SELECT rowid FROM department WHERE company="SoFi" AND name=?;',
            db_data) # nosec B608
        department_id = cursor.fetchone()
    return department_id[0]


def _handle_department(
        department: WebElement) -> tuple[str, list[tuple[str, str]]]:
    """Get data from the department element, like name and positions."""
    dept_name = strip_html_chr(_find_elem_class(
        department, SOFI_DEPARTMENT_TITLE_CLASS).text)
    if dept_name.startswith('CC'):
        dept_name = dept_name[dept_name.index(' ') + 1:]
    positions = _find_elems_class(department, SOFI_POSITION_WRAPPER_CLASS)
    position_results = []
    for position in positions:
        name = strip_html_chr(position.find_element(
            By.CLASS_NAME, value=SOFI_POSITION_TITLE_CLASS
        ).get_attribute('innerHTML'))
        url = position.get_attribute('data-link')
        # location = position.find_element(
        #     By.CLASS_NAME, value='job-location').get_attribute('innerHTML')
        position_results.append((name, url))
    return dept_name, position_results


def _create_company_if_not_exists(conn, cursor, company: Company):
    db_data = (company.name,)
    cursor.execute(
        'SELECT name FROM company WHERE name=?;', db_data) # nosec B608
    if cursor.fetchone() is None:
        cursor.execute(
            'INSERT INTO company VALUES (?);', db_data) # nosec B608
        conn.commit()


def _find_elems_class(objects, class_name):
    return objects.find_elements(By.CLASS_NAME, value=class_name)


def _find_elem_class(objects, class_name):
    return objects.find_element(By.CLASS_NAME, value=class_name)
