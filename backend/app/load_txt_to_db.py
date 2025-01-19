"""Module to load positions from txt files to the database."""

import sqlite3
from datetime import date

from helpers import delete_positions_date, build_db_path


def get_department_rowid_or_create(
        conn, cursor, department: str, company: str) -> int:
    """
        Get the department's rowid, and if needed create it beforehand too.

    :param conn: Database connection.
    :param cursor: Database cursor.
    :param department: The department name.
    :param company: The company name.
    :return: The rowid of the department.
    """
    query_department_rowid(cursor, department, company)
    if (department_id := cursor.fetchone()) is None:
        cursor.execute('INSERT INTO department VALUES '
                       f'("{department}", "{company}");')
        conn.commit()
        query_department_rowid(cursor, department, company)
        department_id = cursor.fetchone()
    return department_id[0]


def query_department_rowid(cursor, department: str, company: str):
    """
        Execute a query to get the rowid of the department from company.

    :param cursor: Database cursor.
    :param department: The required department.
    :param company: The company the department belongs to.
    """
    cursor.execute('SELECT rowid FROM department '
                   f'WHERE name="{department}" AND company="{company}";')


def create_company_if_not_exist(conn, cursor, company: str):
    """
        Check whether the company exists in the database, if not create it.

    :param conn: Database connection.
    :param cursor: Database cursor.
    :param company: Company name.
    """
    # Check if SoFi exists in the company table.
    cursor.execute(f'SELECT name FROM company WHERE name="{company}";')
    if cursor.fetchone() is None:
        # Add SoFi if it doesn't exist.
        cursor.execute(f'INSERT INTO company VALUES ("{company}");')
        conn.commit()


def load_to_db(jobs_date: date, jobs: dict, company: str):
    """
        Load the positions dict into the database.

    :param jobs_date: The date the jobs dict was scraped.
    :param jobs: Dict with positions sorted into departments.
    :param company: The name of the company for the positions.
    """
    with sqlite3.connect(build_db_path(), isolation_level=None) as conn:
        cursor = conn.cursor()
        create_company_if_not_exist(conn, cursor, company)
        delete_positions_date(cursor, jobs_date, company)
        for department in jobs:
            department_id = get_department_rowid_or_create(
                conn, cursor, department, company)
            for position in jobs[department]:
                cursor.execute(
                    'INSERT INTO position VALUES '
                    f'("{position}", "{jobs_date}", {department_id});')
                conn.commit()


def clean_sofi_jobs(jobs: list) -> dict:
    """
        Clean the position listing from the SoFi file.

    :param jobs: List of all the lines in the SoFi position file.
    :return: Dict with positions sorted into departments.
    """
    res = {}
    openings_len = len('OPENINGS')
    department = ''
    while len(jobs) > 0:
        line = jobs.pop(0)
        lower_line = line.lower()
        if lower_line.endswith('openings') or lower_line.endswith('opening'):
            department = line[:line.rindex(' ', 0, (1+openings_len)*(-1))]
            res[department] = []
        elif line != 'Apply Now':
            res[department].append(line)
            if jobs.pop(0) == 'Apply Now':
                jobs.pop(0)
    return res


def clean_galileo_jobs(jobs: list) -> dict:
    """
        Clean the position listing from the Galileo file.

    :param jobs: List of all the lines in the Galileo position file.
    :return: Dict with positions sorted into departments.
    """
    res = {}
    department = ''
    while len(jobs) > 0:
        line = jobs.pop(0)
        lower_line = line.lower()
        if lower_line.startswith('@'):
            department = line[1:]
            res[department] = []
        else:
            res[department].append(line)
    return res


def read_files_db(file_name: str, company: str):
    """
        Read from Galileo positions files and load to the database.

    :param file_name: The name of the file.
    :param company: The name of the company.
    """
    with open(file_name, encoding='utf8') as f:
        lines = f.read().splitlines()
    jobs_date = date.fromisoformat(lines.pop(0).replace('.', '-'))
    if company == 'Galileo':
        jobs = clean_galileo_jobs(lines)
    elif company == 'SoFi':
        jobs = clean_sofi_jobs(lines)
    load_to_db(jobs_date, jobs, company)


def _load_data():
    # read_files_db('prev1.txt', 'SoFi')
    # read_files_db('prev.txt', 'SoFi')
    read_files_db('../../new.txt', 'SoFi')
    # read_files_db('galileo_new.txt', 'Galileo')


if __name__ == '__main__':
    _load_data()
