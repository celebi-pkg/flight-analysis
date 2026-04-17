"""Pytest configuration and fixtures."""

import pytest
import tempfile
import os


@pytest.fixture
def temp_db():
    """Create a temporary database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except:
            pass


@pytest.fixture
def sample_route():
    """Sample route data."""
    return {
        "origin": "JFK",
        "destination": "LAX",
        "departure_date": "2026-05-01",
    }


@pytest.fixture
def sample_flight_data():
    """Sample flight data."""
    return {
        "origin": "JFK",
        "destination": "LAX",
        "departure_date": "2026-05-01",
        "departure_time": "10:00",
        "arrival_time": "13:00",
        "price_cents": 35000,
        "stops": 0,
        "duration": "5h 0m",
    }