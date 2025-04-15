"""Typing module."""
from datetime import date
from typing import Optional

from pydantic import BaseModel


class Company(BaseModel):
    """Company type model."""

    name: str


class Department(BaseModel):
    """Department type model."""

    name: str
    company: Company


class Position(BaseModel):
    """Position type model."""

    name: str
    scrape_date: date
    department: Department
    location: Optional[str] = None
    url: str
