"""Tests for database module."""

import pytest
import tempfile
import os
from datetime import datetime

from google_flight_analysis.db import Database, get_db


class TestDatabase:
    """Test Database class."""
    
    def test_init_database(self, temp_db):
        """Test database initialization."""
        db = Database(temp_db)
        db.initdb()
        
        assert os.path.exists(temp_db)
    
    def test_get_or_create_route(self, temp_db):
        """Test route creation."""
        db = Database(temp_db)
        db.initdb()
        
        route_id = db.get_or_create_route("JFK", "LAX", "one-way")
        
        assert route_id is not None
        assert isinstance(route_id, int)
    
    def test_get_or_create_route_existing(self, temp_db):
        """Test getting existing route."""
        db = Database(temp_db)
        db.initdb()
        
        route_id1 = db.get_or_create_route("JFK", "LAX")
        route_id2 = db.get_or_create_route("JFK", "LAX")
        
        assert route_id1 == route_id2
    
    def test_log_scrape(self, temp_db):
        """Test scrape logging."""
        db = Database(temp_db)
        db.initdb()
        
        route_id = db.get_or_create_route("JFK", "LAX")
        log_id = db.log_scrape(
            route_id=route_id,
            num_flights_found=10,
            num_flights_stored=8,
            success=True,
        )
        
        assert log_id is not None
        assert isinstance(log_id, int)
    
    def test_add_flights(self, temp_db):
        """Test adding flights."""
        db = Database(temp_db)
        db.initdb()
        
        route_id = db.get_or_create_route("JFK", "LAX")
        log_id = db.log_scrape(route_id=route_id, num_flights_found=5, num_flights_stored=5, success=True)
        
        flights_data = [
            {
                "departure_datetime": datetime(2026, 5, 1, 10, 0),
                "arrival_datetime": datetime(2026, 5, 1, 13, 0),
                "departure_airport": "JFK",
                "arrival_airport": "LAX",
                "price_cents": 35000,
                "duration_minutes": 300,
                "stops": 0,
            },
        ]
        
        count = db.add_flights(route_id, log_id, flights_data)
        
        assert count == 1
    
    def test_get_flights(self, temp_db):
        """Test getting flights."""
        db = Database(temp_db)
        db.initdb()
        
        route_id = db.get_or_create_route("JFK", "LAX")
        log_id = db.log_scrape(route_id=route_id, num_flights_found=5, num_flights_stored=5, success=True)
        
        flights_data = [
            {
                "departure_datetime": datetime(2026, 5, 1, 10, 0),
                "arrival_datetime": datetime(2026, 5, 1, 13, 0),
                "departure_airport": "JFK",
                "arrival_airport": "LAX",
                "price_cents": 35000,
                "duration_minutes": 300,
                "stops": 0,
            },
        ]
        
        db.add_flights(route_id, log_id, flights_data)
        
        flights = db.get_flights("JFK", "LAX")
        
        assert len(flights) == 1
        assert flights[0]["departure_airport"] == "JFK"
    
    def test_get_price_history(self, temp_db):
        """Test price history."""
        db = Database(temp_db)
        db.initdb()
        
        route_id = db.get_or_create_route("JFK", "LAX")
        log_id = db.log_scrape(route_id=route_id, num_flights_found=2, num_flights_stored=2, success=True)
        
        flights_data = [
            {
                "departure_datetime": datetime(2026, 5, 1, 10, 0),
                "arrival_datetime": datetime(2026, 5, 1, 13, 0),
                "departure_airport": "JFK",
                "arrival_airport": "LAX",
                "price_cents": 35000,
                "duration_minutes": 300,
                "stops": 0,
            },
            {
                "departure_datetime": datetime(2026, 5, 1, 10, 0),
                "arrival_datetime": datetime(2026, 5, 1, 13, 0),
                "departure_airport": "JFK",
                "arrival_airport": "LAX",
                "price_cents": 40000,
                "duration_minutes": 300,
                "stops": 0,
            },
        ]
        
        db.add_flights(route_id, log_id, flights_data)
        
        history = db.get_price_history("JFK", "LAX", days=30)
        
        assert len(history) > 0
        assert history[0]["min_price"] == 35000
    
    def test_get_active_routes(self, temp_db):
        """Test getting active routes."""
        db = Database(temp_db)
        db.initdb()
        
        db.get_or_create_route("JFK", "LAX")
        db.get_or_create_route("JFK", "SFO")
        
        routes = db.get_active_routes()
        
        assert len(routes) >= 2


class TestGetDb:
    """Test get_db function."""
    
    def test_get_db_singleton(self):
        """Test singleton pattern."""
        db1 = get_db()
        db2 = get_db()
        
        assert db1 is db2