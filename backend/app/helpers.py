"""Helpers module for the backend."""
import pytz
from datetime import date, datetime
from dateutil.relativedelta import relativedelta, FR

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, insert

from .proj_typing import Company, Position, Department
from .models import (Position as db_Position, Department as db_Department,
                     Company as db_Company)


def create_position(db_session, department_id, position: Position):
    """Create database entry for the position."""
    db_session.execute(insert(db_Position).values(
        name=position.name, scrape_date=position.scrape_date, url=position.url,
        department_id=department_id))


def create_and_get_department(
        db_session: Session, department: Department) -> str:
    """Create a department if it doesn't already exist and return id.

    :param db_session: The connection to the sqlalchemy engine.
    :param department: The Department typing object to create in the database.
    :return: The id of the department in the database.
    """
    company_name: str = department.company.name
    db_data: dict[str: str] = {
        'company_name': company_name, 'name': department.name}
    stmt = select(db_Department.id).where(
        (db_Department.name == department.name)
        & (db_Department.company_name == company_name))
    department_id = db_session.execute(stmt).first()
    if department_id is None:
        db_session.execute(insert(db_Department).values(db_data))
        department_id = db_session.execute(stmt).first()
        db_session.commit()
    return department_id[0]


def create_company_if_not_exists(db_session, company: Company):
    """Create a company in the database if it didn't exist.

    :param db_session: Database Session.
    :param company: Company with the data to create the entry.
    """
    stmt = select(db_Company.name).where(db_Company.name == company.name)
    res = db_session.execute(stmt).first()
    if res is None:
        db_session.execute(insert(db_Company).values(name=company.name))
        db_session.commit()


def get_date(*, is_old: bool) -> date:
    """Get the chosen date by the user.

    :param is_old: Whether it is the old date.
    :return: Returns the chosen date as a date object.
    """
    chosen_date = ''
    if is_old:
        input_str = ('Enter date (YYYY.MM.DD) for old date or leave empty for '
                     'last Friday:')
    else:
        input_str = ('Enter date (YYYY.MM.DD) for new date or leave empty for '
                     'today:')
    while not isinstance(chosen_date, date):
        chosen_date = input(input_str)
        if chosen_date == '':
            chosen_date = datetime.now(pytz.timezone('US/Eastern')).date()
            if is_old:
                chosen_date += relativedelta(weekday=FR(-1))
                if (datetime.now(pytz.timezone('US/Eastern')
                                 ).date() == chosen_date):
                    chosen_date += relativedelta(weekday=FR(-2))
        else:
            try:
                chosen_date = chosen_date.replace('.', '-')
                chosen_date = date.fromisoformat(chosen_date)
            except ValueError:
                print('Bad date format')
    return chosen_date


def delete_positions_date(db_session: Session, jobs_date: date,
                          company: Company):
    """Delete positions for a given date in a specific company.

    :param db_session: Database session.
    :param jobs_date: The date for which the positions will be deleted.
    :param company: The company the positions belong to.
    """
    inner_stmt = (select(db_Position.id.label('id')).select_from(db_Position)
                  .join(db_Department,
                        db_Position.department_id == db_Department.id)
                  .where(db_Position.scrape_date == jobs_date,
                         db_Department.company_name == company.name))
    positions = db_session.execute(inner_stmt).fetchall()
    if len(positions) != 0:
        stmt = delete(db_Position).where(db_Position.id.in_(tuple(zip(*positions))[0]))
        db_session.execute(stmt)
