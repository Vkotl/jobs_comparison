import sqlite3
from datetime import date

from helpers import delete_positions_date


def read_files_galileo_db(file_name):
    """
        Read from Galileo positions files and load to the database.
    :param file_name: The name of the file.
    """
    with open(file_name, encoding='utf8') as f:
        lines = f.read().splitlines()
    jobs_date = date.fromisoformat(lines.pop(0).replace('.', '-'))
    jobs = clean_galileo_jobs(lines)

    load_to_db(jobs_date, jobs, 'Galileo')


def get_or_create_company(conn, cursor, company: str):
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


def build_sofi_db():
    """
        Build the tables in the database.
    """
    with sqlite3.connect('sofijobs.db') as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS company '
                       '(name text primary key collate nocase)')
        cursor.execute('CREATE TABLE IF NOT EXISTS department '
                       '(name text, company text, '
                       'foreign key(company) references company(name))')
        cursor.execute('CREATE TABLE IF NOT EXISTS position '
                       '(name text, date text, department integer, '
                       'foreign key(department) references department(rowid))')
        # print_db_schema(cursor)


def print_db_schema(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
        cursor.execute(f'SELECT * FROM {table[0]}')
        print(cursor.description)


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


def clean_jobs(jobs: list) -> dict:
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


def load_to_db(jobs_date: date, jobs: dict, company: str):
    """
        Load the positions dict into the database.
    :param jobs_date: The date the jobs dict was scraped.
    :param jobs: Dict with positions sorted into departments.
    :param company: The name of the company for the positions.
    """
    with sqlite3.connect('sofijobs.db', isolation_level=None) as conn:
        cursor = conn.cursor()
        get_or_create_company(conn, cursor, company)
        delete_positions_date(cursor, jobs_date, company)
        for department in jobs:
            department_id = get_department_rowid_or_create(
                conn, cursor, department, company)
            for position in jobs[department]:
                cursor.execute(
                    'INSERT INTO position VALUES '
                    f'("{position}", "{jobs_date}", {department_id});')
                conn.commit()


def read_files_load_db(file_name):
    """
        Read from SoFi positions files and load to the database.
    :param file_name: The name of the file.
    """
    with open(file_name, encoding='utf8') as f:
        lines = f.read().splitlines()
    jobs_date = date.fromisoformat(lines.pop(0).replace('.', '-'))
    jobs = clean_jobs(lines)
    load_to_db(jobs_date, jobs, 'SoFi')


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
    get_department_rowid(cursor, department, company)
    if (department_id := cursor.fetchone()) is None:
        cursor.execute('INSERT INTO department VALUES '
                       f'("{department}", "{company}");')
        conn.commit()
        get_department_rowid(cursor, department, company)
        department_id = cursor.fetchone()
    return department_id[0]


def get_department_rowid(cursor, department: str, company: str):
    """
        Execute a query to get the rowid of the department from company.
    :param cursor: Database cursor.
    :param department: The required department.
    :param company: The company the department belongs to.
    """
    cursor.execute('SELECT rowid FROM department '
                   f'WHERE name="{department}" AND company="{company}";')


def load_data():
    read_files_load_db('prev1.txt')
    read_files_load_db('prev.txt')
    read_files_load_db('new.txt')
    read_files_galileo_db('galileo_new.txt')


if __name__ == '__main__':
    build_sofi_db()
    load_data()
