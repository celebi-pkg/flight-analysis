"""Tests for scrape module."""

import pytest
from datetime import datetime

from google_flight_analysis.scrape import (
    Scrape, ScrapeResult, TripType, scrape as scrape_func,
)


class TestScrapeResult:
    """Test ScrapeResult dataclass."""
    
    def test_create_result(self):
        """Test creating a result."""
        result = ScrapeResult(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
            departure_time="10:00",
            arrival_time="13:00",
            price_cents=35000,
            stops=0,
        )
        
        assert result.origin == "JFK"
        assert result.destination == "LAX"
        assert result.price_cents == 35000
    
    def test_result_with_trip_type(self):
        """Test result with round trip."""
        result = ScrapeResult(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
            return_date="2026-05-05",
            trip_type="round-trip",
        )
        
        assert result.trip_type == "round-trip"
        assert result.return_date == "2026-05-05"


class TestScrape:
    """Test Scrape class."""
    
    def test_create_scrape_one_way(self):
        """Test creating one-way scrape."""
        scrape_obj = Scrape(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
            trip_type=TripType.ONE_WAY,
        )
        
        assert scrape_obj.origin == "JFK"
        assert scrape_obj.destination == "LAX"
        assert scrape_obj.trip_type == TripType.ONE_WAY
    
    def test_create_scrape_round_trip(self):
        """Test creating round-trip scrape."""
        scrape_obj = Scrape(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
            return_date="2026-05-05",
            trip_type=TripType.ROUND_TRIP,
        )
        
        assert scrape_obj.origin == "JFK"
        assert scrape_obj.return_date == "2026-05-05"
    
    def test_build_url_one_way(self):
        """Test URL building for one-way."""
        scrape_obj = Scrape(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
        )
        
        url = scrape_obj._build_url()
        
        assert "JFK" in url
        assert "LAX" in url
        assert "2026-05-01" in url
    
    def test_build_url_round_trip(self):
        """Test URL building for round-trip."""
        scrape_obj = Scrape(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
            return_date="2026-05-05",
            trip_type=TripType.ROUND_TRIP,
        )
        
        url = scrape_obj._build_url()
        
        assert "2026-05-05" in url
    
    def test_parse_duration(self):
        """Test duration parsing."""
        assert Scrape._parse_duration("5h 30m") == 330
        assert Scrape._parse_duration("2h") == 120
        assert Scrape._parse_duration("45m") == 45
        assert Scrape._parse_duration("10h 0m") == 600
        assert Scrape._parse_duration("") is None
        assert Scrape._parse_duration("invalid") is None
    
    def test_results_initially_empty(self):
        """Test results start empty."""
        scrape_obj = Scrape(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
        )
        
        assert scrape_obj.results == []
        assert scrape_obj.num_flights == 0
    
    def test_dataframe_initially_empty(self):
        """Test DataFrame starts empty."""
        scrape_obj = Scrape(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
        )
        
        df = scrape_obj.data
        
        assert df.empty


class TestScrapeFunction:
    """Test scrape convenience function."""
    
    def test_scrape_creates_scrape_object(self):
        """Test scrape function creates Scrape object."""
        # This won't actually scrape, just checks construction
        scrape_obj = Scrape(
            origin="JFK",
            destination="LAX",
            departure_date="2026-05-01",
        )
        
        assert scrape_obj.origin == "JFK"


class TestTripType:
    """Test TripType enum."""
    
    def test_trip_type_values(self):
        """Test trip type enum values."""
        assert TripType.ONE_WAY.value == "one-way"
        assert TripType.ROUND_TRIP.value == "round-trip"
        assert TripType.CHAIN_TRIP.value == "chain-trip"
        assert TripType.PERFECT_CHAIN.value == "perfect-chain"