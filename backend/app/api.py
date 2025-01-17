"""Main file for running FastAPI."""

from datetime import datetime
from dateutil.relativedelta import relativedelta, FR

import pytz
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .sofi_jobs import scrape_sofi
from .galileo_jobs import scrape_galileo
from .total_jobs import get_last_10_dates
from .compare_positions import get_position_changes

app = FastAPI()

origins = [
    "http://localhost:8000",
    "localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get('/')
def read_root():
    """Handle root URL where it returns last week changes."""
    tz_title = 'US/Eastern'
    chosen_date = datetime.now(pytz.timezone(tz_title)).date()
    old_date = chosen_date + relativedelta(weekday=FR(-1))
    if datetime.now(pytz.timezone(tz_title)).date() == old_date:
        old_date += relativedelta(weekday=FR(-2))
    sofi = get_position_changes(old_date, chosen_date, 'SoFi')
    galileo = get_position_changes(old_date, chosen_date, 'Galileo')
    return {'new_date': chosen_date, 'last_friday': old_date, 'sofi': sofi,
            'galileo': galileo}


@app.get('/changes')
def recent_dates():
    """Display the last 10 dates in the database."""
    print('I am here!')
    return {"last_10": get_last_10_dates()}


@app.get('/changes/{old_date}-{new_date}')
def read_changes(old_date: str, new_date: str):
    """Display the changes between the old date and the new date."""
    old_date = datetime.strptime(old_date, '%Y%m%d')
    new_date = datetime.strptime(new_date, '%Y%m%d')
    if datetime.now(pytz.timezone('US/Eastern')).date() == old_date:
        old_date += relativedelta(weekday=FR(-2))
    sofi = get_position_changes(old_date, new_date, 'SoFi')
    galileo = get_position_changes(old_date, new_date, 'Galileo')
    return {'new_date': new_date.strftime('%Y-%m-%d'),
            'previous_date': old_date.strftime('%Y-%m-%d'), 'sofi': sofi,
            'galileo': galileo}


@app.get('/grab_data')
def grab_data():
    """Scrape positions data from the sites and save in the database."""
    try:
        scrape_sofi()
        scrape_galileo()
    except Exception as e:
        print(e)
        return {'error': "Scraping failed."}
    return {'success': 'Scraping completed.'}
