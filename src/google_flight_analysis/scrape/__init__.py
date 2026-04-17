"""
Scraping module for google-flight-analysis.

Provides classes and functions for scraping flight data from Google Flights.
"""

from google_flight_analysis.scrape.scrape import Scrape, ScrapeResult, TripType, scrape
from google_flight_analysis.scrape.driver import ChromeDriver, DriverConfig, get_driver

__all__ = [
    "Scrape",
    "ScrapeResult",
    "TripType",
    "scrape",
    "ChromeDriver",
    "DriverConfig",
    "get_driver",
]