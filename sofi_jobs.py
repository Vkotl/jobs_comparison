from datetime import date

from helpers import print_difference
from compare_positions import crosscheck_jobs, get_company_jobs


def sofi_jobs_check(old_date: date, new_date: date):
    (old_jobs, old_date), (new_jobs, new_date) = get_company_jobs(
        old_date, new_date, 'SoFi')
    difference = crosscheck_jobs(new_jobs, old_jobs)
    print(f'SoFi changes between {old_date:%Y.%m.%d} and {new_date:%Y.%m.%d}')
    print('New positions:')
    print_difference(difference['new'])
    print('Removed positions:')
    print_difference(difference['removed'])
