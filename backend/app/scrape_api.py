"""Module to define the ScrapeAPI."""
from typing import Optional
from datetime import datetime, date

import pytz
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from .exceptions import FailedScrapeError
from .proj_typing import Company, Department, Position

class ScrapeAPI:
    """API to manage all the scraping for a given company."""

    def __init__(self, company_data: dict, company_name: str):
        """Initialize the Scrape API with company data."""
        self.company: Company = Company(name=company_name)
        self.url: str = company_data['url']
        self.classes: dict[str: str] = company_data['classes']
        self.wait: Optional[dict] = company_data.get('wait', None)


    @staticmethod
    def find_elems_by_class(objects, class_name: str, single: bool = False):
        """Find the elements in objects based on the class name."""
        params = {'value': class_name}
        if class_name.startswith('.'):
            params['by'] = By.CSS_SELECTOR
        else:
            params['by'] = By.CLASS_NAME
        if single:
            return objects.find_element(**params)
        return objects.find_elements(**params)

    def scrape(self) -> list[Position]:
        """Run the scraping for the defined url."""
        positions: list[Position] = []
        with SB(browser='chrome', uc=True, xvfb=True) as sb:
            failed_connection: bool = self._connect_to_page(sb)
            if failed_connection:
                failed_connection = self._connect_to_page(sb)
                if failed_connection:
                    raise FailedScrapeError()
            body: WebElement = sb.find_element('body', by=By.TAG_NAME)
            try:
                departments: list = self.find_elems_by_class(
                    body, self.classes['department wrapper'])
                position_date = datetime.now(
                    pytz.timezone('US/Eastern')).date()
                for department in departments:
                    positions.extend(self.handle_department(
                        department, position_date))
            except TimeoutException:
                print('Failed')
        return positions

    def _connect_to_page(self, sb: SB):
        """Handle connecting to the page and waiting for it to load."""
        sb.uc_open_with_reconnect(self.url, 10)
        attempts = 0
        while not self._is_page_loaded(sb) and attempts < 2:
            sb.uc_gui_click_captcha(retry=True)
            sb.sleep(5)
            attempts += 1
        return attempts == 2 and not self._is_page_loaded(sb)


    def _is_page_loaded(self, sb: SB):
        """Check if the page is ready for scraping."""
        if self.wait is not None:
            if sb.is_element_present(self.wait['element'], by=By.CSS_SELECTOR):
                if 'text' in self.wait:
                    elem = sb.find_element(
                        self.wait['element'], by=By.CSS_SELECTOR)
                    match self.wait['text']:
                        # If the text is the same as "not" then not loaded.
                        case {'not': txt} if txt != elem.text:
                            return True
                        # If the text is the same as "equal" then loaded.
                        case {'equal': elem.text}:
                            return True
                # If no 'text' in self.wait then element only needs to exist.
                else:
                    return True
            return False
        return True

    def handle_department(
            self, department: WebElement, pos_date: date
            ) -> list[Position]:
        """Handle scraping the department data from the site."""
        dept_name: str = self.strip_html_chr(self.find_elems_by_class(
            department, self.classes['department title'], single=True).text)
        dept_name = self.department_parse_enhancement(dept_name)
        dept_obj = Department(name=dept_name, company=self.company)
        positions = self.find_elems_by_class(
            department, self.classes['position wrapper'])
        position_results: list[Position] = []
        for position in positions:
            pos_obj: Optional[Position] = self.position_scrape_controller(
                position, pos_date, dept_obj)
            if pos_obj is not None:
                position_results.append(pos_obj)
        return position_results

    def position_scrape_controller(
        self, position: WebElement,
        scrape_date: date, department: Department) -> Optional[Position]:
        """Manage scraping of positions of different companies."""
        match self.company.name:
            case 'SoFi':
                name: str = self.strip_html_chr(position.find_element(
                    By.CLASS_NAME, value=self.classes['position title']
                ).get_attribute('innerHTML'))
                url: str = position.get_attribute('data-link')
                position_obj = Position(
                    name=name, url=url, scrape_date=scrape_date,
                    department=department)
            case 'Galileo':
                url_element: WebElement = position.find_element(
                    By.TAG_NAME, value='a')
                url: str = url_element.get_attribute('href')
                name: str = self.strip_html_chr(
                    url_element.get_attribute('innerHTML'))
                location: str = self.strip_html_chr(position.find_element(
                    By.TAG_NAME, value='div').get_attribute('innerHTML'))
                position_obj = Position(
                    name=f'{name} ({location})', location=location, url=url,
                    scrape_date=scrape_date, department=department)
            case _:
                position_obj = None
        return position_obj

    @staticmethod
    def strip_html_chr(text: str) -> str:
        """Remove amp; and &nbsp; from texts and then use strip()."""
        replacements = {'amp;': '', '&nbsp;': ' '}
        for key, value in replacements.items():
            if key in text:
                text = text.replace(key, value)
        return text.strip()

    def department_parse_enhancement(self, department_name: str):
        """Additional parsing changes that are company specific."""
        if self.company.name == 'SoFi' and department_name.startswith('CC'):
            return department_name[department_name.index(' ') + 1:]
        return department_name
