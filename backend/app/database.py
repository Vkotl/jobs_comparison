"""Database package."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base
from .constants import DEV_FLAG
from .helpers import build_db_path

engine = create_engine(f'sqlite:///{build_db_path()}', echo=DEV_FLAG)
dbsession = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base.metadata.create_all(engine)

def get_session():
    """Get the database session and handle closing in the end."""
    session = dbsession()
    try:
        yield session
    finally:
        session.close()
