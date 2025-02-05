"""Comparison and data retrival from the database."""
import pytz
import sqlite3
from datetime import date, datetime
from dateutil.relativedelta import relativedelta, FR

from .helpers import build_db_path


def get_data_db(check_date: date, company: str) -> tuple[dict, date]:
    """Get the company data from the database of the given date.

    :param check_date: Date of the data.
    :param company: The company name.
    :return: Data related to the company structured in a dictionary.
    """
    res = {}
    with sqlite3.connect(build_db_path()) as conn:
        cursor = conn.cursor()
        db_data = (check_date.strftime('%Y-%m-%d'), company)
        cursor.execute(
            'SELECT department.name, position.name, position.url '
            'FROM position '
            'INNER JOIN department ON position.department=department.rowid '
            'WHERE position.date=? AND department.company=?;', db_data)
        positions = cursor.fetchall()
        if len(positions) == 0:
            db_data = (company,)
            cursor.execute(
                'SELECT position.date FROM position '
                'INNER JOIN department '
                'ON position.department=department.rowid '
                'WHERE department.company=? '
                'ORDER BY position.date DESC LIMIT 1;', db_data) # nosec B608
            entry_date = cursor.fetchone()
            recent_date = date.fromisoformat(entry_date[0])
            return get_data_db(recent_date, company)
        for position in positions:
            department = position[0]
            pos_data = (position[1],
                        position[2] if position[2] is not None else '')
            if department in res:
                res[department].append(pos_data)
            else:
                res[department] = [pos_data]
    return res, check_date


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


def get_company_jobs(old_date: date, new_date: date, company: str
                     ) -> tuple[tuple[dict, date], tuple[dict, date]]:
    """Get all the positions in the new and old dates from the database.

    :param old_date: Date of the older positions.
    :param new_date: Date of the newer positions.
    :param company: The company name.
    :return: The dates data and the positions.
    """
    return get_data_db(old_date, company), get_data_db(new_date, company)


def print_difference(orig_dict):
    """Print the differences as structured, or print about no changes.

    :param orig_dict: Dictionary of differences.
    """
    if len(orig_dict) != 0:
        for department in orig_dict:
            print(f'  {department}:')
            for pos in orig_dict[department]:
                print(f'    {pos}')
    else:
        print('There are no changes.')


def get_position_changes(old_date: date, new_date: date, company: str) -> dict:
    """Retrieve the changes between positions in those two dates for company.

    :param old_date: The old date to use for the old positions.
    :param new_date: The new date to use for the new positions.
    :param company: The company name that the positions belong to.
    :return: Dictionary of changes.
    """
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, company)
    difference = crosscheck_jobs(new_jobs, old_jobs)
    return difference


def handle_changes_response(old_date: date, new_date: date) -> dict:
    """Handle the response with positions changes."""
    if datetime.now(pytz.timezone('US/Eastern')).date() == old_date:
        old_date += relativedelta(weekday=FR(-2))
    sofi = get_position_changes(old_date, new_date, 'SoFi')
    galileo = get_position_changes(old_date, new_date, 'Galileo')
    return {'new_date': new_date.strftime('%Y-%m-%d'),
            'previous_date': old_date.strftime('%Y-%m-%d'), 'sofi': sofi,
            'galileo': galileo}
