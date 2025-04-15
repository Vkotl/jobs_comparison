"""Main file for running FastAPI."""

from datetime import datetime
from dateutil.relativedelta import relativedelta, FR

import pytz
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .database import get_session
from .total_jobs import get_last_10_dates, scrape_and_create_positions
from .decorators import date_verification
from .compare_positions import handle_changes_response

app = FastAPI()

origins = [
    'http://localhost:8000',
    'localhost:8000'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@app.get('/changes/week')
@date_verification
def changes_week(db_session: Session = Depends(get_session)):
    """Handle root URL where it returns last week changes."""
    tz_title = 'US/Eastern'
    chosen_date = datetime.now(pytz.timezone(tz_title)).date()
    old_date = chosen_date + relativedelta(weekday=FR(-1))
    return handle_changes_response(db_session, old_date, chosen_date)


@app.get('/changes')
def recent_dates(db_session: Session = Depends(get_session)):
    """Display the last 10 dates in the database."""
    return {'last_10': get_last_10_dates(db_session)}


@app.get('/changes/{old_date}-{new_date}')
@date_verification
def changes_two_dates(old_date: str, new_date: str,
                      db_session: Session = Depends(get_session)):
    """Display the changes between the old date and the new date."""
    print(old_date, new_date)
    old_date = datetime.strptime(old_date, '%Y%m%d').date()
    new_date = datetime.strptime(new_date, '%Y%m%d').date()
    return handle_changes_response(db_session, old_date, new_date)


@app.get('/changes/{new_date}')
@date_verification
def changes_single_date(new_date: str,
                        db_session: Session = Depends(get_session)):
    """Display the changes the new date and previous Friday."""
    new_date = datetime.strptime(new_date, '%Y%m%d')
    old_date = new_date + relativedelta(weekday=FR(-1))
    if new_date == old_date:
        old_date += relativedelta(weekday=FR(-2))
    return handle_changes_response(db_session, old_date, new_date)


@app.post('/grab_data')
def grab_data(db_session: Session = Depends(get_session)):
    """Scrape positions data from the sites and save in the database."""
    try:
        scrape_and_create_positions(db_session, 'SoFi')
        scrape_and_create_positions(db_session, 'Galileo', delay=15)
    except Exception as e:
        print(e)
        return {'error': 'Scraping failed.'}
    return {'success': 'Scraping completed.'}
