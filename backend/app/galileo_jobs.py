"""Handle scraping and writing to database the Galileo positions."""
import pytz
from datetime import date, datetime

from sqlalchemy.orm import Session
from sqlalchemy import text, select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

# from .exceptions import CompanyNotInDatabaseError
from .helpers import delete_positions_date, strip_amp
from .proj_typing import Company, Department, Position
from .models import Department as db_Department, Company as db_Company
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


def scrape_galileo(db_session: Session):
    """Scrape the Galileo positions from the site."""
    driver = webdriver.Firefox()
    driver.implicitly_wait(time_to_wait=20)
    driver.get(GALILEO_CAREERS_URL)
    try:
        departments = _find_elems_class(
            driver, GALILEO_DEPARTMENT_WRAPPER_CLASS)
        # with sqlite3.connect(build_db_path()) as conn:
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
                'date': position.date.strftime('%Y-%m-%d'),
               'depart_id': department_id, 'url': position.url}
    stmt = text(
        'INSERT INTO position VALUES (:name, :date, :deprt_id, :url);'
    )
    stmt = stmt.bindparams(**db_data)
    db_session.execute(stmt)


def _create_department_get(db_session: Session, department: Department) -> int:
    """Create a department if it doesn't already exist and return id.

    :param conn: The connection to the sqlalchemy engine.
    :param department: The department typing object to create in the database.
    :return: The id of the department in the database.
    """
    company_name: str = department.company.name
    db_data: dict[str: str] = {'comp': company_name, 'name': department.name}
    # stmt = text('SELECT rowid FROM department '
    #             'WHERE company=:comp AND name=:name;')
    # stmt = stmt.bindparams(**db_session)
    stmt = select(db_Department.id).where(
        (db_Department.company == company_name)
        & (db_Department.name == department.name))
    department_id = db_session.execute(stmt).first()
    if department_id is None:
        # company = db_session.execute(
        #     select(db_Company).where(db_Company.name == company_name)).first()
        # if company is None:
        #     raise CompanyNotInDatabase()
        #
        # db_Department(name=department.name, company=company)
        insert_stmt = text('INSERT INTO department (company, name) '
                    'VALUES (:comp, :name);')
        insert_stmt = insert_stmt.bindparams(**db_data)
        db_session.execute(insert_stmt)
        department_id = db_session.execute(stmt).first()
        # department_id = cursor.fetchone()
    return department_id[0]


def _create_company_if_not_exists(db_session, company: Company):
    # stmt = text('SELECT name FROM company WHERE name=:name;')
    # stmt = stmt.bindparams(name=company.name)
    res = db_session.execute(
        select(db_Company).where(db_Company.name==company.name))
    # res = db_session.execute(stmt)
    if res.first() is None:
        stmt = text('INSERT INTO company VALUES (:name);')
        stmt = stmt.bindparams(name=company.name)
        db_session.execute(stmt)
        db_session.commit()
