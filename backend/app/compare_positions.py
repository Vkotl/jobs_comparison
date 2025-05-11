"""Comparison and data retrival from the database."""
from datetime import date
from dateutil.relativedelta import relativedelta, FR

from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func

from .constants import DATE_FORMAT_DB
from .models import Department, Position
from .helpers import get_today_date, get_previous_friday


def get_data_db(
    db_session: Session, check_date: date, company: str) -> tuple[dict, date]:
    """Get the company data from the database of the given date.

    :param db_session: SQLAlchemy session.
    :param check_date: Date of the data.
    :param company: The company name.
    :return: Data related to the company structured in a dictionary.
    """
    res = {}
    stmt = select(Department.name, Position.name, Position.url).select_from(
        Position).join(Department, Position.department_id == Department.id
    ).where(Position.scrape_date == check_date,
            Department.company_name == company)
    query_res = db_session.execute(stmt).all()
    if len(query_res) == 0:
        stmt = select(Position.scrape_date).select_from(Position).join(
            Department, Position.department_id == Department.id
        ).where(Department.company_name == company).order_by(
            desc(Position.scrape_date)).limit(1)
        entry_date = db_session.execute(stmt).fetchone()
        return get_data_db(db_session, entry_date[0], company)
    for position in query_res:
        department = position[0]
        pos_name = position[1]
        pos_data = (pos_name,
                    position[2] if position[2] is not None else '',
                    is_brand_new(db_session, company, department, pos_name))
        if department in res:
            res[department].append(pos_data)
        else:
            res[department] = [pos_data]
    return res, check_date


def is_brand_new(
    db_session: Session, company: str, department: str, position: str) -> bool:
    """Check if a position appears for the first time in the department."""
    stmt = select(func.count()).select_from(Position).join(
        Department, Position.department_id == Department.id).where(
        Department.name == department, Position.name == position,
        Department.company_name == company,
        Position.scrape_date <= get_previous_friday())
    count = db_session.execute(stmt).fetchone()[0]
    return count == 1


def crosscheck_jobs(new_jobs: dict, old_jobs: dict) -> dict:
    """Return which positions are new and which are removed/filled.

    :param new_jobs: Dictionary of the open positions in the "new" date.
    :param old_jobs: Dictionary of the open positions in the "old" date.
    :return: Dictionary of the new positions and the removed positions.
    """
    res = {'new': {}, 'removed': {}}
    new_pos = res['new']
    removed_pos = res['removed']
    _handle_comparison(new_jobs, old_jobs, new_pos)
    _handle_comparison(old_jobs, new_jobs, removed_pos)
    return res


def _handle_comparison(from_lst, to_lst, diff_dict):
    for department in from_lst:
        if department not in to_lst:
            diff_dict[department] = from_lst[department]
        else:
            diff_dict[department] = []
            for pos in from_lst[department]:
                try:
                    next(filter(lambda item: pos[0] == item[0],
                                to_lst[department]))
                except StopIteration:
                    diff_dict[department].append(pos)
            if len(diff_dict[department]) == 0:
                del diff_dict[department]


def get_company_jobs(
    db_session: Session, old_date: date, new_date: date, company: str
    ) -> tuple[tuple[dict, date], tuple[dict, date]]:
    """Get all the positions in the new and old dates from the database.

    :param db_session: SQLAlchemy session.
    :param old_date: Date of the older positions.
    :param new_date: Date of the newer positions.
    :param company: The company name.
    :return: The dates data and the positions.
    """
    return (get_data_db(db_session, old_date, company),
            get_data_db(db_session, new_date, company))


def get_position_changes(
    db_session: Session, old_date: date, new_date: date, company: str) -> dict:
    """Retrieve the changes between positions in those two dates for company.

    :param db_session: SQLAlchemy session.
    :param old_date: The old date to use for the old positions.
    :param new_date: The new date to use for the new positions.
    :param company: The company name that the positions belong to.
    :return: Dictionary of changes.
    """
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        db_session, old_date, new_date, company)
    difference = crosscheck_jobs(new_jobs, old_jobs)
    return difference


def handle_changes_response(
    db_session: Session, old_date: date, new_date: date) -> dict:
    """Handle the response with positions changes."""
    if get_today_date() == old_date:
        old_date += relativedelta(weekday=FR(-2))
    companies = ('SoFi', 'Galileo')
    res = {}
    for company in companies:
        res[company.lower()] = get_position_changes(
            db_session, old_date, new_date, company)
    return {'new_date': new_date.strftime(DATE_FORMAT_DB),
            'previous_date': old_date.strftime(DATE_FORMAT_DB), **res}
