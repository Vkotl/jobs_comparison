import sqlite3


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


if __name__ == '__main__':
    build_sofi_db()
