import sqlite3
from datetime import date


def get_data_db(check_date: date, company: str) -> tuple[dict, date]:
    res = {}
    with sqlite3.connect('sofijobs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT department.name, position.name FROM position '
                       'INNER JOIN department '
                       'ON position.department=department.rowid '
                       f'WHERE position.date="{check_date:%Y-%m-%d}" '
                       f'AND department.company="{company}";')
        positions = cursor.fetchall()
        if len(positions) == 0:
            cursor.execute(
                'SELECT position.date FROM position '
                'INNER JOIN department '
                'ON position.department=department.rowid '
                f'WHERE department.company="{company}" '
                f'ORDER BY position.date DESC LIMIT 1;')
            entry_date = cursor.fetchone()
            recent_date = date.fromisoformat(entry_date[0])
            return get_data_db(recent_date, company)
        for position in positions:
            department = position[0]
            if department in res:
                res[department].append(position[1])
            else:
                res[department] = [position[1]]
    return res, check_date


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


def get_company_jobs(old_date: date, new_date: date, company: str
                     ) -> tuple[tuple[dict, date], tuple[dict, date]]:
    return get_data_db(old_date, company), get_data_db(new_date, company)
