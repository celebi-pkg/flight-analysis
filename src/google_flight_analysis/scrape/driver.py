"""
Chrome driver wrapper for scraping Google Flights.

Provides a clean interface for ChromeDriver operations with retry logic
and proper resource management.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Optional
from contextlib import contextmanager

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
)

from google_flight_analysis import config as app_config

logger = logging.getLogger(__name__)


@dataclass
class DriverConfig:
    """Configuration for Chrome driver."""
    headless: bool = True
    no_sandbox: bool = True
    disable_dev_shm_usage: bool = True
    disable_gpu: bool = True
    window_size: str = "1920,1080"
    wait: int = 10
    page_load_timeout: int = 30
    implicit_wait: int = 5


class ChromeDriver:
    """Chrome driver wrapper with retry logic."""
    
    def __init__(self, config: Optional[DriverConfig] = None):
        """Initialize driver."""
        self.config = config or DriverConfig()
        self._driver: Optional[webdriver.Chrome] = None
        self._wait: Optional[WebDriverWait] = None
    
    def _get_options(self) -> Options:
        """Get Chrome options."""
        options = Options()
        
        if self.config.headless:
            options.add_argument("--headless")
        if self.config.no_sandbox:
            options.add_argument("--no-sandbox")
        if self.config.disable_dev_shm_usage:
            options.add_argument("--disable-dev-shm-usage")
        if self.config.disable_gpu:
            options.add_argument("--disable-gpu")
        
        options.add_argument(f"--window-size={self.config.window_size}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        return options
    
    def start(self) -> None:
        """Start the Chrome driver."""
        try:
            chromedriver_autoinstaller.install()
        except Exception as e:
            logger.warning(f"Could not install chromedriver: {e}")
        
        options = self._get_options()
        
        try:
            self._driver = webdriver.Chrome(options=options)
        except WebDriverException as e:
            logger.error(f"Failed to start Chrome: {e}")
            raise
        
        self._driver.set_page_load_timeout(self.config.page_load_timeout)
        self._driver.implicitly_wait(self.config.implicit_wait)
        
        self._wait = WebDriverWait(self._driver, self.config.wait)
        
        logger.info("Chrome driver started")
    
    def get(self, url: str) -> None:
        """Navigate to URL."""
        if self._driver is None:
            self.start()
        self._driver.get(url)
    
    def wait_for_element(self, by: str, value: str, timeout: Optional[int] = None):
        """Wait for element to be present."""
        if self._wait is None:
            self._wait = WebDriverWait(self._driver, timeout or self.config.wait)
        
        return self._wait.until(
            EC.presence_of_element_located((by, value)),
            message=f"Element not found: {value}"
        )
    
    def wait_for_elements(self, by: str, value: str, timeout: Optional[int] = None):
        """Wait for elements to be present."""
        if self._wait is None:
            self._wait = WebDriverWait(self._driver, timeout or self.config.wait)
        
        return self._wait.until(
            EC.presence_of_all_elements_located((by, value)),
            message=f"Elements not found: {value}"
        )
    
    def find_element(self, by: str, value: str):
        """Find single element."""
        if self._driver is None:
            raise RuntimeError("Driver not started")
        return self._driver.find_element(by, value)
    
    def find_elements(self, by: str, value: str):
        """Find multiple elements."""
        if self._driver is None:
            raise RuntimeError("Driver not started")
        return self._driver.find_elements(by, value)
    
    def execute_script(self, script: str, *args):
        """Execute JavaScript."""
        if self._driver is None:
            raise RuntimeError("Driver not started")
        return self._driver.execute_script(script, *args)
    
    def wait(self, seconds: float = 1.0) -> None:
        """Explicit wait."""
        time.sleep(seconds)
    
    def quit(self) -> None:
        """Quit the driver."""
        if self._driver is not None:
            try:
                self._driver.quit()
            except Exception as e:
                logger.warning(f"Error quitting driver: {e}")
            finally:
                self._driver = None
                self._wait = None
                logger.info("Chrome driver stopped")
    
    @property
    def driver(self) -> Optional[webdriver.Chrome]:
        """Get the underlying driver."""
        return self._driver
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.quit()


@contextmanager
def get_driver(config: Optional[DriverConfig] = None):
    """Context manager for driver."""
    driver = ChromeDriver(config)
    try:
        driver.start()
        yield driver
    finally:
        driver.quit()