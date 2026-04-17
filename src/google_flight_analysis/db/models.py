"""
Database models for google-flight-analysis.

Defines SQLAlchemy models for flight data, routes, and scrape logs.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, DateTime, Boolean, Index, ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TripType(enum.Enum):
    """Trip type enumeration."""
    ONE_WAY = "one-way"
    ROUND_TRIP = "round-trip"
    CHAIN_TRIP = "chain-trip"
    PERFECT_CHAIN = "perfect-chain"


class Flight(Base):
    """Flight data model."""
    __tablename__ = "flights"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    scrape_log_id = mapped_column(Integer, ForeignKey("scrape_logs.id"), nullable=False)
    
    departure_datetime = mapped_column(DateTime, nullable=False)
    arrival_datetime = mapped_column(DateTime, nullable=True)
    
    departure_airport = mapped_column(String(3), nullable=False)
    arrival_airport = mapped_column(String(3), nullable=False)
    
    airline = mapped_column(String(10), nullable=True)
    flight_number = mapped_column(String(10), nullable=True)
    
    duration_minutes = mapped_column(Integer, nullable=True)
    stops = mapped_column(Integer, default=0)
    
    price_cents = mapped_column(Integer, nullable=True)
    currency = mapped_column(String(3), default="USD")
    
    emissions_kg = mapped_column(Integer, nullable=True)
    
    raw_data = mapped_column(String(1000), nullable=True)
    
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_flight_route_scrape", "route_id", "scrape_log_id"),
        Index("idx_flight_route_date", "route_id", "departure_datetime"),
        Index("idx_flight_price", "route_id", "price_cents", "departure_datetime"),
    )


class Route(Base):
    """Route model."""
    __tablename__ = "routes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin = mapped_column(String(3), nullable=False)
    destination = mapped_column(String(3), nullable=False)
    
    trip_type = mapped_column(String(20), default="one-way")
    
    is_active = mapped_column(Boolean, default=True)
    
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_route_orig_dest", "origin", "destination"),
    )


class ScrapeLog(Base):
    """Scrape log model - tracks when scraping occurred."""
    __tablename__ = "scrape_logs"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    
    scraped_at = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    num_flights_found = mapped_column(Integer, default=0)
    num_flights_stored = mapped_column(Integer, default=0)
    
    success = mapped_column(Boolean, default=False)
    error_message = mapped_column(String(500), nullable=True)
    
    duration_seconds = mapped_column(Float, nullable=True)
    
    created_at = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_scrape_log_route_time", "route_id", "scraped_at"),
    )


class ConfigValue(Base):
    """Key-value store for configuration."""
    __tablename__ = "config_values"

    key = mapped_column(String(100), primary_key=True)
    value = mapped_column(String(500), nullable=False)
    description = mapped_column(String(500), nullable=True)
    updated_at = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SubscriptionRoute(Base):
    """Subscription model for routes to track."""
    __tablename__ = "subscription_routes"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    
    email = mapped_column(String(255), nullable=False)
    
    departure_date_start = mapped_column(String(10), nullable=True)
    departure_date_end = mapped_column(String(10), nullable=True)
    
    max_price_cents = mapped_column(Integer, nullable=True)
    
    is_active = mapped_column(Boolean, default=True)
    
    notify_on_drop = mapped_column(Boolean, default=True)
    
    created_at = mapped_column(DateTime, default=datetime.utcnow)
    updated_at = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )