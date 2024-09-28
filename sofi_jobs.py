import sqlite3
from datetime import date


def crosscheck_jobs(new_jobs, old_jobs) -> dict:
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
                if pos not in to_lst[department]:
                    diff_dict[department].append(pos)
            if len(diff_dict[department]) == 0:
                del diff_dict[department]


def print_difference(orig_dict):
    if len(orig_dict) != 0:
        for department in orig_dict:
            print(f'  {department}:')
            for pos in orig_dict[department]:
                print(f'    {pos}')
    else:
        print('There are no changes.')


def get_data_db(check_date: date) -> dict:
    res = {}
    with sqlite3.connect('sofijobs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT department, name FROM position '
                       f'WHERE date="{check_date:%Y-%m-%d}"')
        for position in cursor.fetchall():
            department = position[0]
            if department in res:
                res[department].append(position[1])
            else:
                res[department] = [position[1]]
    return res


def main():
    old_date = date(year=2024, month=9, day=20)
    new_date = date(year=2024, month=9, day=27)
    old_jobs = get_data_db(old_date)
    new_jobs = get_data_db(new_date)
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'Change between {old_date:%Y.%m.%d} and {new_date:%Y.%m.%d}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])


if __name__ == '__main__':
    main()
