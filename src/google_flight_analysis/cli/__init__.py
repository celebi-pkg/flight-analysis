"""
CLI module for google-flight-analysis.

Provides the command-line interface for interacting with the package.
"""

from google_flight_analysis.cli.main import cli
from google_flight_analysis.cli.commands import (
    price,
    scrape_cmd,
    db_cmd,
    analyze_cmd,
    recommend,
)

__all__ = [
    "cli",
    "price",
    "scrape_cmd",
    "db_cmd",
    "analyze_cmd",
    "recommend",
]
