"""
Legacy module - Houses deprecated but potentially reusable components.

This module contains the original configuration and scraping logic that was working
at some point. It can be used as a fallback or reference if the main scraping
mechanism breaks due to Google Flights UI changes.

Usage:
    from google_flight_analysis.legacy import config as legacy_config
    from google_flight_analysis.legacy import chrome_wrapper as legacy_driver
"""

from google_flight_analysis.legacy.config import chrome_driver as legacy_chrome_driver
from google_flight_analysis.legacy.config import instructions as legacy_instructions
from google_flight_analysis.legacy import scrape as legacy_scrape
from google_flight_analysis.legacy import cache as legacy_cache

__all__ = [
    "legacy_chrome_driver",
    "legacy_instructions",
    "legacy_scrape",
    "legacy_cache",
]