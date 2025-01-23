"""Helpers module for the backend."""
import pytz
from pathlib import Path
from datetime import date, datetime
from dateutil.relativedelta import relativedelta, FR

from .constants import DB_NAME
from .proj_typing import Company


def get_date(*, is_old: bool) -> date:
    """
        Get the chosen date by the user.

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


def delete_positions_date(cursor, jobs_date: date, company: Company):
    """
        Delete positions for a given date in a specific company.

    :param cursor: Database cursor.
    :param jobs_date: The date for which the positions will be deleted.
    :param company: The company the positions belong to.
    """
    cursor.execute(
        'DELETE FROM position '
        'WHERE rowid in ('
        '    SELECT position.rowid as rowid from position '
        '    INNER JOIN department '
        '    ON position.department=department.rowid '
        f'   WHERE position.date="{jobs_date:%Y-%m-%d}" '
        f'   AND department.company="{company.name}");'
    )


def build_db_path() -> Path:
    """Build the database path."""
    return Path(__file__).parents[1].absolute() / DB_NAME
