"""Typing module."""
import datetime
from typing import Optional

from pydantic import BaseModel


class Company(BaseModel):
    """Companies model."""

    name: str


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
