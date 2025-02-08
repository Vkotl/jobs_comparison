"""Typing module."""
import datetime
from typing import Optional, LiteralString

from pydantic import BaseModel


class Company(BaseModel):
    """Companies model."""

    name: LiteralString


class Department(BaseModel):
    """Departments model."""

    name: str
    company: Company


class Position(BaseModel):
    """Positions model."""

    name: str
    date: datetime.date
    department: Department
    location: Optional[str]
    url: str
