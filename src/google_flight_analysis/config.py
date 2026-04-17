"""
Configuration for google-flight-analysis.

This module provides the main configuration for the package, including:
- Chrome driver settings
- Database configuration
- Scraping settings
- Route configurations
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import os


DEFAULT_DB_PATH = os.environ.get(
    "FLIGHT_DB_PATH",
    str(Path.home() / ".flight_analysis" / "flights.db")
)

DEFAULT_CACHE_DIR = os.environ.get(
    "FLIGHT_CACHE_DIR",
    str(Path.home() / ".flight_analysis" / "cache")
)


@dataclass
class ChromeConfig:
    """Chrome driver configuration."""
    options: list = field(default_factory=lambda: [
        "--no-sandbox",
        "--headless",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ])
    wait: int = 10
    page_load_timeout: int = 30
    implicit_wait: int = 5


@dataclass
class ScrapeConfig:
    """Scraping configuration."""
    max_retries: int = 3
    retry_delay: int = 2
    min_wait_between_requests: int = 5
    batch_size: int = 10
    timeout: int = 30


@dataclass
class DBConfig:
    """Database configuration."""
    path: str = DEFAULT_DB_PATH
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class Config:
    """Main configuration object."""
    chrome: ChromeConfig = field(default_factory=ChromeConfig)
    scrape: ScrapeConfig = field(default_factory=ScrapeConfig)
    db: DBConfig = field(default_factory=DBConfig)
    cache_dir: str = DEFAULT_CACHE_DIR


config = Config()


def get_config() -> Config:
    """Get the global configuration object."""
    return config


def update_config(**kwargs) -> Config:
    """Update configuration values."""
    for key, value in kwargs.items():
        if hasattr(config, key):
            if isinstance(value, dict):
                sub_config = getattr(config, key)
                for sub_key, sub_value in value.items():
                    if hasattr(sub_config, sub_key):
                        setattr(sub_config, sub_key, sub_value)
            else:
                setattr(config, key, value)
    return config