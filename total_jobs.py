import sqlite3
from helpers import get_date, compare_positions


def print_last_10_dates():
    with sqlite3.connect('sofijobs.db') as conn:
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
    with sqlite3.connect('sofijobs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT date from position '
                       'ORDER BY date DESC LIMIT 10;')
        dates = cursor.fetchall()
        res = []
        for pos_date in dates[::-1]:
            res.append(pos_date[0])
        return res


def main():
    print_last_10_dates()
    old_date = get_date(is_old=True)
    new_date = get_date(is_old=False)
    compare_positions(old_date, new_date, 'SoFi')
    compare_positions(old_date, new_date, 'Galileo')


if __name__ == '__main__':
    main()
