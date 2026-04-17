"""
Database models for google-flight-analysis.

Defines SQLAlchemy models for flight data, routes, and scrape logs.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, Float, DateTime, Boolean, Index, ForeignKey, Enum as SQLEnum,
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    scrape_log_id: Mapped[int] = mapped_column(Integer, ForeignKey("scrape_logs.id"), nullable=False)
    
    departure_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    arrival_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    departure_airport: Mapped[str] = mapped_column(String(3), nullable=False)
    arrival_airport: Mapped[str] = mapped_column(String(3), nullable=False)
    
    airline: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    flight_number: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stops: Mapped[int] = mapped_column(Integer, default=0)
    
    price_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    emissions_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    raw_data: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    route: Mapped["Route"] = relationship("Route", back_populates="flights")
    scrape_log: Mapped["ScrapeLog"] = relationship("ScrapeLog", back_populates="flights")

    __table_args__ = (
        Index("idx_flight_route_scrape", "route_id", "scrape_log_id"),
        Index("idx_flight_route_date", "route_id", "departure_datetime"),
        Index("idx_flight_price", "route_id", "price_cents", "departure_datetime"),
    )


class Route(Base):
    """Route model."""
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    origin: Mapped[str] = mapped_column(String(3), nullable=False)
    destination: Mapped[str] = mapped_column(String(3), nullable=False)
    
    trip_type: Mapped[str] = mapped_column(
        SQLEnum(TripType, native_enum=False),
        default=TripType.ONE_WAY.value
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    flights: Mapped[list["Flight"]] = relationship(
        "Flight", back_populates="route", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_route_orig_dest", "origin", "destination"),
    )


class ScrapeLog(Base):
    """Scrape log model - tracks when scraping occurred."""
    __tablename__ = "scrape_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    
    scraped_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    num_flights_found: Mapped[int] = mapped_column(Integer, default=0)
    num_flights_stored: Mapped[int] = mapped_column(Integer, default=0)
    
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    route: Mapped["Route"] = relationship("Route", back_populates="scrape_logs")
    flights: Mapped[list["Flight"]] = relationship(
        "Flight", back_populates="scrape_log", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_scrape_log_route_time", "route_id", "scraped_at"),
    )


class ConfigValue(Base):
    """Key-value store for configuration."""
    __tablename__ = "config_values"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class SubscriptionRoute(Base):
    """Subscription model for routes to track."""
    __tablename__ = "subscription_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    
    departure_date_start: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    departure_date_end: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    max_price_cents: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    notify_on_drop: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )