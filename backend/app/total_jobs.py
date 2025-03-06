"""Module to combine both Galileo and SoFi job treatment modules."""
import sqlite3

from .helpers import build_db_path


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
