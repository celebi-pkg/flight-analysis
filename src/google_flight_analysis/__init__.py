"""
google-flight-analysis - Flight scraping and price analysis.

A Python package for scraping flight data from Google Flights and analyzing
flight prices with forecasting capabilities.
"""

__version__ = "2.0.0"

from google_flight_analysis.db import Database, get_db
from google_flight_analysis.db import Flight, Route, ScrapeLog
from google_flight_analysis.scrape import (
    ChromeDriver,
    DriverConfig,
    Scrape,
    ScrapeResult,
    TripType,
    get_driver,
    scrape,
)

__all__ = [
    "ChromeDriver",
    "Database",
    "DriverConfig",
    "Flight",
    "get_db",
    "get_driver",
    "Route",
    "Scrape",
    "ScrapeLog",
    "ScrapeResult",
    "TripType",
    "scrape",
    "__version__",
]
