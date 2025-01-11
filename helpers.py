import pytz
from datetime import date, datetime
from dateutil.relativedelta import relativedelta, FR

from compare_positions import crosscheck_jobs, get_company_jobs


def get_date(*, is_old: bool) -> date:
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
                if (datetime.now(pytz.timezone('US/Eastern')).date()
                        == chosen_date):
                    chosen_date += relativedelta(weekday=FR(-2))
        else:
            try:
                chosen_date = chosen_date.replace('.', '-')
                chosen_date = date.fromisoformat(chosen_date)
            except ValueError:
                print('Bad date format')
    return chosen_date


def print_difference(orig_dict):
    if len(orig_dict) != 0:
        for department in orig_dict:
            print(f'  {department}:')
            for pos in orig_dict[department]:
                print(f'    {pos}')
    else:
        print('There are no changes.')


def delete_positions_date(cursor, jobs_date: date, company: str):
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
        f'   AND department.company="{company}");'
    )


def compare_positions(old_date: date, new_date: date, company: str):
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, company)
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'{company} changes between {old_date:%Y.%m.%d} and '
          f'{new_date:%Y.%m.%d}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])


def return_position_changes(old_date: date, new_date: date, company: str):
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, company)
    difference = crosscheck_jobs(new_jobs, old_jobs)
    return difference
