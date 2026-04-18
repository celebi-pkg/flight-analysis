"""
Main scraping module for Google Flights.

Provides the Scrape class for querying and scraping flight data from Google Flights.
"""

import logging
import time
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
from urllib.parse import quote

import pandas as pd

from google_flight_analysis.scrape.driver import ChromeDriver, DriverConfig
from google_flight_analysis.db import get_db

logger = logging.getLogger(__name__)


class TripType(Enum):
    """Trip type enumeration."""

    ONE_WAY = "one-way"
    ROUND_TRIP = "round-trip"
    CHAIN_TRIP = "chain-trip"
    PERFECT_CHAIN = "perfect-chain"


@dataclass
class ScrapeResult:
    """Result of a scrape operation."""

    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None

    departure_airport: str = ""
    arrival_airport: str = ""
    departure_time: str = ""
    arrival_time: str = ""
    airline: str = ""
    flight_number: str = ""
    duration: str = ""
    stops: int = 0
    price_cents: Optional[int] = None
    currency: str = "USD"
    emissions_kg: Optional[int] = None

    trip_type: str = "one-way"
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    raw_data: dict = field(default_factory=dict)


class Scrape:
    """Main scrape class for Google Flights."""

    BASE_URL = "https://www.google.com/travel/flights"

    def __init__(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        trip_type: TripType = TripType.ONE_WAY,
    ):
        """Initialize scrape object."""
        self.origin = origin.upper()
        self.destination = destination.upper()
        self.departure_date = departure_date
        self.return_date = return_date
        self.trip_type = trip_type or TripType.ONE_WAY

        self._driver: Optional[ChromeDriver] = None
        self._results: List[ScrapeResult] = []
        self._df: Optional[pd.DataFrame] = None

    def _build_url(self) -> str:
        """Build the Google Flights URL."""
        params = [
            f"from={self.origin}",
            f"to={self.destination}",
            f"date={self.departure_date}",
        ]

        if self.trip_type == TripType.ROUND_TRIP and self.return_date:
            params.append(f"return={self.return_date}")

        if self.trip_type == TripType.ONE_WAY:
            params.append("oneway=true")

        query = "&".join(params)
        return f"{self.BASE_URL}?hl=en&q={quote(query)}"

    def _wait_for_content(self, driver: ChromeDriver, timeout: int = 20) -> bool:
        """Wait for page content to load."""
        try:
            driver.wait_for_element("css selector", "body", timeout=timeout)
            driver.wait(timeout=2)
            return True
        except Exception as e:
            logger.warning(f"Timeout waiting for content: {e}")
            return False

    def _extract_flights(self, driver: ChromeDriver) -> List[ScrapeResult]:
        """Extract flight data from page."""
        results = []

        try:
            from selenium.webdriver.common.by import By

            flight_cards = driver.find_elements(
                "xpath", "//li[contains(@class, 'pIav2d')] | //div[contains(@class, 'flight-card')]"
            )

            for card in flight_cards:
                try:
                    result = self._extract_flight_card(card)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.debug(f"Error extracting card: {e}")
                    continue

            if not results:
                results = self._extract_fallback(driver)

        except Exception as e:
            logger.error(f"Error extracting flights: {e}")

        return results

    def _extract_flight_card(self, card) -> Optional[ScrapeResult]:
        """Extract data from a single flight card."""
        try:
            from selenium.webdriver.common.by import By

            result = ScrapeResult(
                origin=self.origin,
                destination=self.destination,
                departure_date=self.departure_date,
                return_date=self.return_date,
                trip_type=self.trip_type.value,
            )

            result.departure_airport = self.origin
            result.arrival_airport = self.destination

            try:
                times = card.find_elements(By.CSS_SELECTOR, "[class*='time']")
                if times:
                    result.departure_time = times[0].text
                if len(times) > 1:
                    result.arrival_time = times[1].text
            except Exception:
                pass

            try:
                price_elem = card.find_element(
                    "xpath", ".//span[contains(text(), '$')] | .//div[contains(@class, 'price')]"
                )
                price_text = price_elem.text
                price_match = re.search(r"[\d,]+", price_text.replace("$", ""))
                if price_match:
                    result.price_cents = int(price_match.group().replace(",", ""))
            except Exception:
                pass

            try:
                duration_elem = card.find_element("xpath", ".//div[contains(@class, 'duration')]")
                result.duration = duration_elem.text
            except Exception:
                pass

            try:
                stops_elem = card.find_element("xpath", ".//div[contains(@class, 'stops')]")
                stops_text = stops_elem.text.lower()
                if "nonstop" in stops_text or "direct" in stops_text:
                    result.stops = 0
                else:
                    stops_match = re.search(r"(\d+)\s*stop", stops_text)
                    result.stops = int(stops_match.group(1)) if stops_match else 0
            except Exception:
                pass

            return result

        except Exception as e:
            logger.debug(f"Error parsing card: {e}")
            return None

    def _extract_fallback(self, driver: ChromeDriver) -> List[ScrapeResult]:
        """Fallback extraction using page text."""
        results = []

        try:
            page_text = driver.driver.page_source

            price_pattern = r"\$[\d,]+"
            prices = re.findall(price_pattern, page_text)

            for i, price in enumerate(prices[:10]):
                result = ScrapeResult(
                    origin=self.origin,
                    destination=self.destination,
                    departure_date=self.departure_date,
                    return_date=self.return_date,
                    trip_type=self.trip_type.value,
                )

                price_match = re.search(r"[\d,]+", price)
                if price_match:
                    result.price_cents = int(price_match.group().replace(",", ""))

                results.append(result)

        except Exception as e:
            logger.error(f"Fallback extraction error: {e}")

        return results

    def execute(
        self,
        driver: Optional[ChromeDriver] = None,
        use_driver_context: bool = True,
    ) -> List[ScrapeResult]:
        """Execute the scrape."""
        start_time = time.time()

        if driver:
            self._driver = driver
            use_driver_context = False

        try:
            if use_driver_context:
                with ChromeDriver() as driver:
                    return self._execute(driver, start_time)
            else:
                return self._execute(driver, start_time)

        except Exception as e:
            logger.error(f"Scrape error: {e}")
            raise

    def _execute(self, driver: ChromeDriver, start_time: float) -> List[ScrapeResult]:
        """Internal execute method."""
        url = self._build_url()
        logger.info(f"Scraping: {url}")

        driver.get(url)

        if not self._wait_for_content(driver):
            logger.warning("Page content may not have loaded fully")

        self._results = self._extract_flights(driver)

        duration = time.time() - start_time
        logger.info(f"Found {len(self._results)} flights in {duration:.2f}s")

        return self._results

    def to_dataframe(self) -> pd.DataFrame:
        """Convert results to DataFrame."""
        if not self._results:
            return pd.DataFrame()

        data = []
        for result in self._results:
            data.append(
                {
                    "origin": result.origin,
                    "destination": result.destination,
                    "departure_date": result.departure_date,
                    "return_date": result.return_date,
                    "departure_airport": result.departure_airport,
                    "arrival_airport": result.arrival_airport,
                    "departure_time": result.departure_time,
                    "arrival_time": result.arrival_time,
                    "airline": result.airline,
                    "flight_number": result.flight_number,
                    "duration": result.duration,
                    "stops": result.stops,
                    "price_cents": result.price_cents,
                    "currency": result.currency,
                    "emissions_kg": result.emissions_kg,
                    "trip_type": result.trip_type,
                    "scraped_at": result.scraped_at,
                }
            )

        self._df = pd.DataFrame(data)
        return self._df

    @property
    def data(self) -> pd.DataFrame:
        """Get data as DataFrame."""
        if self._df is None:
            return self.to_dataframe()
        return self._df

    @property
    def results(self) -> List[ScrapeResult]:
        """Get raw results."""
        return self._results

    @property
    def num_flights(self) -> int:
        """Get number of flights found."""
        return len(self._results)

    def save_to_db(self, db_path: Optional[str] = None) -> int:
        """Save results to database."""
        if not self._results:
            logger.warning("No results to save")
            return 0

        db = get_db(db_path)

        route = db.get_or_create_route(self.origin, self.destination, self.trip_type.value)

        log = db.log_scrape(
            route_id=route.id,
            num_flights_found=len(self._results),
            num_flights_stored=len(self._results),
            success=True,
        )

        flights_data = []
        for result in self._results:
            dep_dt = datetime.strptime(
                f"{result.departure_date} {result.departure_time}", "%Y-%m-%d %H:%M"
            )
            arr_dt = None
            if result.arrival_time:
                try:
                    arr_dt = datetime.strptime(
                        f"{result.departure_date} {result.arrival_time}", "%Y-%m-%d %H:%M"
                    )
                except Exception:
                    pass

            flights_data.append(
                {
                    "departure_datetime": dep_dt,
                    "arrival_datetime": arr_dt,
                    "departure_airport": result.departure_airport,
                    "arrival_airport": result.arrival_airport,
                    "airline": result.airline,
                    "flight_number": result.flight_number,
                    "duration_minutes": self._parse_duration(result.duration),
                    "stops": result.stops,
                    "price_cents": result.price_cents,
                    "currency": result.currency,
                    "emissions_kg": result.emissions_kg,
                }
            )

        count = db.add_flights(route.id, log.id, flights_data)
        logger.info(f"Saved {count} flights to database")

        return count

    @staticmethod
    def _parse_duration(duration: str) -> Optional[int]:
        """Parse duration string to minutes."""
        if not duration:
            return None

        match = re.search(r"(\d+)h\s*(\d+)m", duration.lower())
        if match:
            return int(match.group(1)) * 60 + int(match.group(2))

        match = re.search(r"(\d+)h", duration.lower())
        if match:
            return int(match.group(1)) * 60

        match = re.search(r"(\d+)m", duration.lower())
        if match:
            return int(match.group(1))

        return None


def scrape(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    trip_type: str = "one-way",
) -> Scrape:
    """Convenience function to scrape flights."""
    trip_type_enum = TripType(trip_type)

    scrape_obj = Scrape(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        trip_type=trip_type_enum,
    )

    scrape_obj.execute()

    return scrape_obj


__all__ = [
    "Scrape",
    "ScrapeResult",
    "TripType",
    "scrape",
]
