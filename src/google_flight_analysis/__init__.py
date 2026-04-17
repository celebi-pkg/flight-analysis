"""
google-flight-analysis - Flight scraping and price analysis.

A Python package for scraping flight data from Google Flights and analyzing
flight prices with forecasting capabilities.
"""

__version__ = "2.0.0"

from google_flight_analysis.scrape import Scrape, ScrapeResult, TripType, scrape
from google_flight_analysis.scrape import ChromeDriver, DriverConfig, get_driver
from google_flight_analysis.db import Database, get_db
from google_flight_analysis.db import Flight, Route, ScrapeLog

__all__ = [
    "Scrape",
    "ScrapeResult",
    "TripType",
    "scrape",
    "ChromeDriver",
    "DriverConfig",
    "get_driver",
    "Database",
    "get_db",
    "Flight",
    "Route",
    "ScrapeLog",
    "__version__",
]