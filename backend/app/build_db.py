"""Module for creating and also printing the schema of the database."""
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# import sqlite3
#
# from helpers import build_db_path


# def build_sofi_db():
#     """Build the tables in the database."""
#     with sqlite3.connect(build_db_path()) as conn:
#         cursor = conn.cursor()
#         cursor.execute('CREATE TABLE IF NOT EXISTS company '
#                        '(name text primary key collate nocase)')
#         cursor.execute('CREATE TABLE IF NOT EXISTS department '
#                        '(name text, company text, '
#                        'foreign key(company) references company(name))')
#         cursor.execute(
#             'CREATE TABLE IF NOT EXISTS position '
#             '(name text, date text, department integer, '
#             'foreign key(department) references department(rowid))')
#         # print_db_schema(cursor)


def print_db_schema(cursor):
    """Print the schema of the database."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
        cursor.execute(f'SELECT * FROM {table[0]}') # nosec B608
        print(cursor.description)


# def handle_db_creation():
#     engine = create_engine('sqlite:///./sqlite.db', echo=False)
#     # with Session(engine) as session:


# if __name__ == '__main__':
#     handle_db_creation()
