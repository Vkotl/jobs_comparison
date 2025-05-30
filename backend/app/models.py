"""Database models and database creation."""
from typing import List
from datetime import date

from sqlalchemy import String, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class Company(Base):
    """Company model."""

    __tablename__ = 'company'

    name: Mapped[str] = mapped_column(
        String(10), primary_key=True)

    departments: Mapped[List['Department']] = relationship(
        back_populates='company', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'Company(name={self.name})'


class Department(Base):
    """Department model."""

    __tablename__ = 'department'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    company_name: Mapped[str] = mapped_column(ForeignKey('company.name'))

    company: Mapped['Company'] = relationship(back_populates='departments')
    positions: Mapped[List['Position']] = relationship(
        back_populates='department', cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f'Department(name={self.name}) of {self.company}'


class Position(Base):
    """Position model."""

    __tablename__ = 'position'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200))
    scrape_date: Mapped[date] = mapped_column(Date, nullable=False)
    url: Mapped[str] = mapped_column(String(300), nullable=True)
    department_id: Mapped[int] = mapped_column(ForeignKey('department.id'))

    department: Mapped['Department'] = relationship(back_populates='positions')

    def __repr__(self) -> str:
        return (f'Position(name={self.name}) of '
                f'{self.department.name} {{{self.scrape_date}}}')
