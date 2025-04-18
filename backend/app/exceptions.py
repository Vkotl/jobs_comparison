"""Exceptions module."""

class CompanyNotInDatabaseError(Exception):
    """The company is not in the database."""

    def __init__(self, *args, **kwargs):
        """Exception constructor."""
        if len(args) == 0:
            super().__init__('Company was not found in database.', **kwargs)
        else:
            super().__init__(*args, **kwargs)


class CompanyNotInJSONError(Exception):
    """The company is not in the company JSON file."""

    def __init__(self, *args, **kwargs):
        """Exception constructor."""
        if len(args) == 0:
            super().__init__(
                'Company was not found in company.json.', **kwargs)
        else:
            super().__init__(*args, **kwargs)


class FailedScrapeError(Exception):
    """The company is not in the company JSON file."""

    def __init__(self, *args, **kwargs):
        """Exception constructor."""
        if len(args) == 0:
            super().__init__('Failed to scrape the site', **kwargs)
        else:
            super().__init__(*args, **kwargs)
