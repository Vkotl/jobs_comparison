"""Database package."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .helpers import build_db_path

class Base(DeclarativeBase):
    """Base class for all database models."""

    pass

engine = create_engine(f'sqlite:///{build_db_path()}', echo=True)
Session = sessionmaker(bind=engine)
session = Session(autocommit=False)
Base.metadata.create_all(engine)
