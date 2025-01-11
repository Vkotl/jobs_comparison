from distutils.dep_util import newer
from typing import Union
from datetime import datetime
from dateutil.relativedelta import relativedelta, FR

import pytz
from fastapi import FastAPI

from sofi_jobs import scrape_sofi
from galileo_jobs import scrape_galileo
from total_jobs import get_last_10_dates
from helpers import return_position_changes

app = FastAPI()

@app.get('/')
def read_root():
    chosen_date = datetime.now(pytz.timezone('US/Eastern')).date()
    old_date = chosen_date + relativedelta(weekday=FR(-1))
    if datetime.now(pytz.timezone('US/Eastern')).date() == old_date:
        old_date += relativedelta(weekday=FR(-2))
    sofi = return_position_changes(old_date, chosen_date, 'SoFi')
    galileo = return_position_changes(old_date, chosen_date, 'Galileo')
    return {'new_date': chosen_date, 'last_friday': old_date, 'sofi': sofi,
            'galileo': galileo}


# @app.get('/items/{item_id}')
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

@app.get('/changes')
def recent_dates():
    return {"last_10": get_last_10_dates()}

@app.get('/changes/{date_str}')
def read_changes(date_str: str):
    old_date, new_date = date_str.split('-')
    old_date = datetime.strptime(old_date, '%Y%m%d')
    new_date = datetime.strptime(new_date, '%Y%m%d')
    if datetime.now(pytz.timezone('US/Eastern')).date() == old_date:
        old_date += relativedelta(weekday=FR(-2))
    sofi = return_position_changes(old_date, new_date, 'SoFi')
    galileo = return_position_changes(old_date, new_date, 'Galileo')
    return {'new_date': new_date.strftime('%Y-%m-%d'),
            'previous_date': old_date.strftime('%Y-%m-%d'), 'sofi': sofi,
            'galileo': galileo}


@app.get('/grab_data')
def grab_data():
    try:
        scrape_sofi()
        scrape_galileo()
    except Exception as e:
        return {'error': 'Scraping failed.'}
    return {'success': 'Scraping completed.'}