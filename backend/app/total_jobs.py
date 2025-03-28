"""Module to combine both Galileo and SoFi job treatment modules."""
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from .models import Position


def get_last_10_dates(db_session: Session) -> list[str]:
    """Retrieve the last 10 dates from the database."""
    stmt = select(Position.scrape_date).distinct().order_by(
        desc(Position.scrape_date)).limit(10)
    dates = db_session.execute(stmt)
    res = []
    for pos_date in dates:
        res.append(pos_date[0])
    return res[::-1]
