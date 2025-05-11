"""Main file for running FastAPI."""

import sys
import asyncio
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .database import get_session
from .constants import DATE_FORMAT_URL
from .exceptions import FailedScrapeError
from .decorators import date_verification
from .compare_positions import handle_changes_response
from .helpers import get_previous_friday, get_today_date
from .total_jobs import get_last_10_dates, scrape_and_create_positions

app = FastAPI()
router = APIRouter(prefix='/api')

# SeleniumBase flag that tells it to use thread-locking.
sys.argv.append('-n')

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


@router.get('/changes/week')
@date_verification
def changes_week(db_session: Session = Depends(get_session)):
    """Handle root URL where it returns last week changes."""
    chosen_date = get_today_date()
    old_date = get_previous_friday(chosen_date)
    return handle_changes_response(db_session, old_date, chosen_date)


@router.get('/changes')
def recent_dates(db_session: Session = Depends(get_session)):
    """Display the last 10 dates in the database."""
    return {'last_10': get_last_10_dates(db_session)}


@router.get('/changes/{old_date}-{new_date}')
@date_verification
def changes_two_dates(old_date: str, new_date: str,
                      db_session: Session = Depends(get_session)):
    """Display the changes between the old date and the new date."""
    old_date = datetime.strptime(old_date, DATE_FORMAT_URL).date()
    new_date = datetime.strptime(new_date, DATE_FORMAT_URL).date()
    return handle_changes_response(db_session, old_date, new_date)


@router.get('/changes/{new_date}')
@date_verification
def changes_single_date(new_date: str,
                        db_session: Session = Depends(get_session)):
    """Display the changes the new date and previous Friday."""
    new_date = datetime.strptime(new_date, DATE_FORMAT_URL).date()
    old_date = get_previous_friday(new_date)
    return handle_changes_response(db_session, old_date, new_date)


@router.post('/grab_data')
async def grab_data(db_session: Session = Depends(get_session)):
    """Scrape positions data from the sites and save in the database."""
    try:
        loop = asyncio.get_event_loop()
        companies = ('SoFi', 'Galileo')
        executor = ThreadPoolExecutor(max_workers=len(companies))
        tasks = [loop.run_in_executor(
            executor, scrape_and_create_positions, db_session, company)
            for company in companies]
        await asyncio.gather(*tasks)
    except FailedScrapeError as e:
        traceback.print_exception(e)
        return {'error': 'Scraping failed.'}
    except Exception as e:
        traceback.print_exception(e)
        return {'error': 'Server exception occurred.'}
    return {'success': 'Scraping completed.'}


app.include_router(router)
