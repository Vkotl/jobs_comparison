"""Module to combine both Galileo and SoFi job treatment modules."""
import json
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from .scrape_api import ScrapeAPI
from .models import Position, Department
from .constants import APP_FOLDER, COMPANY_JSON
from .exceptions import CompanyNotInJSONError
from .helpers import (
    create_and_get_department, create_position, delete_positions_date,
    create_company_if_not_exists)


def get_last_10_dates(db_session: Session) -> list[str]:
    """Retrieve the last 10 dates from the database."""
    stmt = select(Position.scrape_date).distinct().order_by(
        desc(Position.scrape_date)).limit(10)
    dates = db_session.execute(stmt)
    res = []
    for pos_date in dates:
        res.append(pos_date[0])
    return res[::-1]


def scrape_and_create_positions(db_session: Session, company_name: str):
    """Scrape the company site and save the data in the database."""
    with Path(APP_FOLDER, COMPANY_JSON).open() as f:
        data = json.load(f).get(company_name, None)
    if data is None:
        raise CompanyNotInJSONError()
    attempts = 0
    positions: dict[Department, list[Position]] = {}
    while len(positions) == 0 and attempts <= 1:
        scraper = ScrapeAPI(data, company_name)
        positions = scraper.scrape()
        attempts += 1
    company = scraper.company
    if len(positions) > 0:
        create_company_if_not_exists(db_session, company)
        delete_positions_date(
            db_session, next(iter(positions.values()))[0].scrape_date, company)
        for department in positions:
            department_id = create_and_get_department(db_session, department)
            for position in positions[department]:
                create_position(db_session, department_id, position)
        db_session.commit()
