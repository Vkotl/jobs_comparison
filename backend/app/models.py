"""Database models and database creation."""
from typing import List
from pathlib import Path
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Company(Base):
    """Company model."""

    __tablename__ = 'company'

    name: Mapped[str] = mapped_column(String(10, collation='NOCASE'),
                                      primary_key=True)

    departments: Mapped[List['Department']] = relationship(
        back_populates='company', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'Company(name={self.name})'


class Department(Base):
    """Department model."""

    __tablename__ = 'department'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    company_name: Mapped[str] = mapped_column(ForeignKey('company.name'))

    company: Mapped['Company'] = relationship(back_populates='departments')
    positions: Mapped[List['Position']] = relationship(
        back_populates='department', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'Department(name={self.name}) of {self.company}'


class Position(Base):
    """Position model."""

    __tablename__ = 'position'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    date: Mapped[datetime] = mapped_column()
    department_name: Mapped[str] = mapped_column(ForeignKey('department.name'))

    department: Mapped['Department'] = relationship(back_populates='positions')

    def __repr__(self) -> str:
        return f'Position(name={self.name}) of {self.department}'


engine = create_engine(
    f'sqlite:///{Path(__file__).parent}/db.sqlite', echo=True)
Session = sessionmaker(bind=engine)
session = Session(autocommit=False)
Base.metadata.create_all(engine)
