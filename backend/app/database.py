"""Database package."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base
from .constants import DEV_FLAG, MYSQL_DEPLOYMENT


def _db_connection_string() -> str:
    """Create the database connection string."""
    credentials = f'{os.environ['MYSQL_USER']}:{os.environ['MYSQL_ROOT_PASSWORD']}'
    db_name = os.environ['MYSQL_DATABASE']
    db_location = f'{MYSQL_DEPLOYMENT}:{os.environ['MYSQL_PORT']}'
    return f'mysql+mysqlconnector://{credentials}@{db_location}/{db_name}'


def get_session():
    """Get the database session and handle closing in the end."""
    session = dbsession()
    try:
        yield session
    finally:
        session.close()


engine = create_engine(_db_connection_string(), echo=DEV_FLAG)
dbsession = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base.metadata.create_all(engine)
