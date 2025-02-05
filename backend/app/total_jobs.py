"""Module to combine both Galileo and SoFi job treatment modules."""
from datetime import date

import sqlite3

from .helpers import get_date, build_db_path
from .compare_positions import (
    print_difference, crosscheck_jobs, get_company_jobs)


def print_last_10_dates():
    """Print the last 10 dates from the database."""
    with sqlite3.connect(build_db_path()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT date from position '
                       'ORDER BY date DESC LIMIT 10;')
        dates = cursor.fetchall()
        for pos_date in dates[::-1]:
            if pos_date != dates[0]:
                print(pos_date[0], end=', ')
            else:
                print(pos_date[0])


def get_last_10_dates():
    """Retrieve the last 10 dates from the database."""
    print('I am inside getting last 10 dates')
    with sqlite3.connect(build_db_path()) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT date from position '
                       'ORDER BY date DESC LIMIT 10;')
        dates = cursor.fetchall()
        res = []
        for pos_date in dates[::-1]:
            res.append(pos_date[0])
        return res


def compare_positions(old_date: date, new_date: date, company: str):
    """Compare and print position differences for a given date and a company.

    :param old_date: The old date to use for the old positions.
    :param new_date: The new date to use for the new positions.
    :param company: The company name that the positions belong to.
    """
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, company)
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'{company} changes between {old_date:%Y.%m.%d} and '
          f'{new_date:%Y.%m.%d}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])


def _main():
    print_last_10_dates()
    old_date = get_date(is_old=True)
    new_date = get_date(is_old=False)
    for company in ('SoFi', 'Galileo'):
        compare_positions(old_date, new_date, company)


if __name__ == '__main__':
    _main()
