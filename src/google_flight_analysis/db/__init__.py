"""
Database module for google-flight-analysis.

Provides SQLite database management with SQLAlchemy for storing
flight data scraped from Google Flights.
"""

from google_flight_analysis.db.database import Database, get_db
from google_flight_analysis.db.models import Flight, Route, ScrapeLog

__all__ = [
    "Database",
    "get_db",
    "Flight",
    "Route",
    "ScrapeLog",
]