"""Handle scraping and writing to database the Galileo positions."""
import pytz
from datetime import date, datetime

import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from .proj_typing import Company, Department, Position
from .helpers import delete_positions_date, build_db_path, strip_amp
from .constants import (
    GALILEO_CAREERS_URL, GALILEO_DEPARTMENT_WRAPPER_CLASS,
    GALILEO_DEPARTMENT_TITLE_CLASS, GALILEO_POSITION_WRAPPER_CLASS)


def _handle_department(
        department: WebElement, company: Company, pos_date: date
) -> list[Position]:
    dept_name = _find_elem_class(
        department, GALILEO_DEPARTMENT_TITLE_CLASS).text
    dept_obj = Department(name=dept_name, company=company)
    positions = _find_elems_class(department, GALILEO_POSITION_WRAPPER_CLASS)
    position_results = []
    for position in positions:
        url_element = position.find_element(By.TAG_NAME, value='a')
        url = url_element.get_attribute('href')
        name = strip_amp(url_element.get_attribute('innerHTML'))
        location = strip_amp(position.find_element(
            By.TAG_NAME, value='div').get_attribute('innerHTML'))
        position_results.append(
            Position(name=name, location=location, department=dept_obj,
                     date=pos_date, url=url))
    return position_results


def scrape_galileo():
    """Scrape the Galileo positions from the site."""
    driver = webdriver.Firefox()
    driver.implicitly_wait(time_to_wait=20)
    driver.get(GALILEO_CAREERS_URL)
    try:
        departments = _find_elems_class(
            driver, GALILEO_DEPARTMENT_WRAPPER_CLASS)
        with sqlite3.connect(build_db_path()) as conn:
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
    except TimeoutException:
        print('Failed')
    driver.close()


def _find_elems_class(objects, class_name):
    return objects.find_elements(By.CLASS_NAME, value=class_name)


def _find_elem_class(objects, class_name):
    return objects.find_element(By.CLASS_NAME, value=class_name)


def _create_position(cursor, department_id, position: Position):
    db_data = (f'{position.name} ({position.location})',
               position.date.strftime('%Y-%m-%d'), department_id, position.url)
    cursor.execute(
        'INSERT INTO position VALUES (?, ?, ?, ?);', db_data) # nosec B608


def _create_department_get(cursor, department: Department) -> int:
    """Create a department if it doesn't already exist and return id.

    :param cursor: Database cursor.
    :param department: The department typing object to create in the database.
    :return: The id of the department in the database.
    """
    company_name = department.company.name
    db_data = (company_name, department.name)
    cursor.execute('SELECT rowid FROM department WHERE company=? AND name=?;',
                   db_data) # nosec B608
    if (department_id := cursor.fetchone()) is None:
        cursor.execute('INSERT INTO department (company, name) VALUES (?, ?);',
                       db_data) # nosec B608
        cursor.execute('SELECT rowid FROM department '
                       'WHERE company=? AND name=?;', db_data) # nosec B608
        department_id = cursor.fetchone()
    return department_id[0]


def _create_company_if_not_exists(conn, cursor, company: Company):
    db_data = (company.name,)
    cursor.execute(
        'SELECT name FROM company WHERE name=?;', db_data) # nosec B608
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO company VALUES (?);', db_data) # nosec B608
        conn.commit()
