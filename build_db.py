import sqlite3


def build_sofi_db():
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
        print_db_schema(cursor)


def print_db_schema(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
        cursor.execute(f'SELECT * FROM {table[0]}')
        print(cursor.description)


def clean_jobs(jobs: list) -> dict:
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


def read_files_load_db(file_name):
    with open(file_name, encoding='utf8') as f:
        lines = f.read().splitlines()
    jobs_date = lines.pop(0).replace('.', '-')
    jobs = clean_jobs(lines)

    with sqlite3.connect('sofijobs.db', isolation_level=None) as conn:
        cursor = conn.cursor()
        # Check if SoFi exists in the company table.
        cursor.execute('SELECT name FROM company WHERE name="SoFi";')
        if cursor.fetchone() is None:
            # Add SoFi if it doesn't exist.
            cursor.execute('INSERT INTO company VALUES ("SoFi");')
            conn.commit()
        # Clear previous history of positions.
        cursor.execute(f'DELETE FROM position WHERE date="{jobs_date}"')
        for department in jobs:
            get_department_rowid(cursor, department)
            if (department_id := cursor.fetchone()) is None:
                cursor.execute('INSERT INTO department VALUES '
                               f'("{department}", "SoFi");')
                conn.commit()
                get_department_rowid(cursor, department)
                department_id = cursor.fetchone()
            for position in jobs[department]:
                cursor.execute(
                    'INSERT INTO position VALUES '
                    f'("{position}", "{jobs_date}", {department_id[0]});')
                conn.commit()
            cursor.execute('SELECT * FROM position')


def get_department_rowid(cursor, department):
    cursor.execute('SELECT rowid FROM department '
                   f'WHERE name="{department}" AND company="SoFi";')


def load_data():
    read_files_load_db('prev1.txt')
    read_files_load_db('prev.txt')
    read_files_load_db('new.txt')


if __name__ == '__main__':
    build_sofi_db()
    load_data()
