"""Handle scraping and writing to database the Galileo positions."""
import pytz
from datetime import date, datetime

from selenium import webdriver
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from .helpers import delete_positions_date, strip_amp
from .proj_typing import Company, Department, Position
from .models import (
    Department as db_Department, Company as db_Company,
    Position as db_Position)
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
                     scrape_date=pos_date, url=url))
    return position_results


def scrape_galileo(db_session: Session):
    """Scrape the Galileo positions from the site."""
    driver = webdriver.Firefox()
    driver.implicitly_wait(time_to_wait=20)
    driver.get(GALILEO_CAREERS_URL)
    try:
        departments = _find_elems_class(
            driver, GALILEO_DEPARTMENT_WRAPPER_CLASS)
        company = Company(name='Galileo')
        _create_company_if_not_exists(db_session, company)
        position_date = datetime.now(pytz.timezone('US/Eastern')).date()
        delete_positions_date(db_session, position_date, company)
        for department in departments:
            position_data = _handle_department(
                department, company, position_date)
            department_id = _create_department_get(
                db_session, position_data[0].department)
            for position in position_data:
                _create_position(db_session, department_id, position)
        db_session.commit()
    except TimeoutException:
        print('Failed')
    driver.close()


def _find_elems_class(objects, class_name):
    return objects.find_elements(By.CLASS_NAME, value=class_name)


def _find_elem_class(objects, class_name):
    return objects.find_element(By.CLASS_NAME, value=class_name)


def _create_position(db_session: Session, department_id, position: Position):
    db_data = {'name': f'{position.name} ({position.location})',
               'scrape_date': position.scrape_date,
               'department_id': department_id, 'url': position.url}
    db_session.execute(insert(db_Position).values(db_data))


def _create_department_get(db_session: Session, department: Department) -> str:
    """Create a department if it doesn't already exist and return id.

    :param conn: The connection to the sqlalchemy engine.
    :param department: The department typing object to create in the database.
    :return: The id of the department in the database.
    """
    company_name: str = department.company.name
    db_data: dict[str: str] = {
        'company_name': company_name, 'name': department.name}
    stmt = select(db_Department.id).where(
        (db_Department.company_name == company_name)
        & (db_Department.name == department.name))
    department_id = db_session.execute(stmt).first()
    if department_id is None:
        db_session.execute(insert(db_Department).values(db_data))
        department_id = db_session.execute(stmt).first()
    return department_id[0]


def _create_company_if_not_exists(db_session, company: Company):
    res = db_session.execute(
        select(db_Company).where(db_Company.name==company.name))
    if res.first() is None:
        db_session.execute(insert(db_Company).values(name=company.name))
        db_session.commit()
