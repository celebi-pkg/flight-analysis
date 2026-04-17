"""
google-flight-analysis - Flight scraping and price analysis.

A Python package for scraping flight data from Google Flights and analyzing
flight prices with forecasting capabilities.
"""

__version__ = "2.0.0"

from google_flight_analysis.scrape import Scrape, ScrapeObjects
from google_flight_analysis.db import Database, get_db

__all__ = [
    "Scrape",
    "ScrapeObjects",
    "Database",
    "get_db",
    "__version__",
]