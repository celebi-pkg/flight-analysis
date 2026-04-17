"""
Database management for google-flight-analysis.

Provides Database class for managing SQLite connections with SQLAlchemy,
including session handling, migrations, and common operations.
"""

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional
import logging

from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from google_flight_analysis.db.models import (
    Base, Flight, Route, ScrapeLog, ConfigValue, TripType,
)
from google_flight_analysis import config as app_config

logger = logging.getLogger(__name__)


class Database:
    """Database manager class."""
    
    def __init__(self, db_path: Optional[str] = None, echo: bool = False):
        """Initialize database connection."""
        self.db_path = db_path or app_config.DEFAULT_DB_PATH
        self.echo = echo
        self._engine = None
        self._session_factory = None
        
    @property
    def engine(self):
        """Lazy-create engine."""
        if self._engine is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._engine = create_engine(
                f"sqlite:///{self.db_path}",
                echo=self.echo,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        return self._engine
    
    @property
    def session_factory(self):
        """Lazy-create session factory."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions."""
        sess = self.session_factory()
        try:
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            sess.close()
    
    def create_tables(self) -> None:
        """Create all tables."""
        Base.metadata.create_all(self.engine)
        logger.info(f"Created tables at {self.db_path}")
    
    def drop_tables(self) -> None:
        """Drop all tables."""
        Base.metadata.drop_all(self.engine)
        logger.info(f"Dropped tables at {self.db_path}")
    
    def initdb(self) -> None:
        """Initialize database (create or reset)."""
        self.drop_tables()
        self.create_tables()
        logger.info(f"Initialized database at {self.db_path}")
    
    def get_or_create_route(
        self, origin: str, destination: str, trip_type: str = "one-way"
    ) -> Route:
        """Get existing route or create new one."""
        with self.session() as sess:
            stmt = select(Route).where(
                Route.origin == origin.upper(),
                Route.destination == destination.upper(),
            )
            route = sess.scalar(stmt)
            if route is None:
                route = Route(
                    origin=origin.upper(),
                    destination=destination.upper(),
                    trip_type=trip_type,
                )
                sess.add(route)
                sess.flush()
            return route
    
    def log_scrape(
        self,
        route_id: int,
        num_flights_found: int,
        num_flights_stored: int,
        success: bool,
        error_message: Optional[str] = None,
        duration_seconds: Optional[float] = None,
    ) -> ScrapeLog:
        """Log a scrape operation."""
        with self.session() as sess:
            log = ScrapeLog(
                route_id=route_id,
                scraped_at=datetime.utcnow(),
                num_flights_found=num_flights_found,
                num_flights_stored=num_flights_stored,
                success=success,
                error_message=error_message,
                duration_seconds=duration_seconds,
            )
            sess.add(log)
            sess.flush()
            return log
    
    def add_flights(
        self,
        route_id: int,
        scrape_log_id: int,
        flights_data: list[dict],
    ) -> int:
        """Add flights to database."""
        with self.session() as sess:
            count = 0
            for flight_data in flights_data:
                flight = Flight(
                    route_id=route_id,
                    scrape_log_id=scrape_log_id,
                    **flight_data
                )
                sess.add(flight)
                count += 1
            return count
    
    def get_flights(
        self,
        origin: str,
        destination: str,
        departure_date: Optional[str] = None,
        limit: int = 100,
    ) -> list[Flight]:
        """Get flights for a route."""
        with self.session() as sess:
            route = sess.scalar(select(Route).where(
                Route.origin == origin.upper(),
                Route.destination == destination.upper(),
            ))
            if route is None:
                return []
            
            stmt = select(Flight).where(Flight.route_id == route.id)
            if departure_date:
                stmt = stmt.where(Flight.departure_datetime.startswith(departure_date))
            stmt = stmt.order_by(Flight.departure_datetime.desc()).limit(limit)
            return list(sess.execute(stmt).scalars().all())
    
    def get_latest_price(
        self, origin: str, destination: str, departure_date: str
    ) -> Optional[int]:
        """Get the latest price for a route and date."""
        with self.session() as sess:
            route = sess.scalar(select(Route).where(
                Route.origin == origin.upper(),
                Route.destination == destination.upper(),
            ))
            if route is None:
                return None
            
            stmt = select(Flight).where(
                Flight.route_id == route.id,
                Flight.departure_datetime.startswith(departure_date),
            ).order_by(Flight.created_at.desc()).limit(1)
            flight = sess.scalar(stmt)
            return flight.price_cents if flight else None
    
    def get_price_history(
        self,
        origin: str,
        destination: str,
        days: int = 30,
    ) -> list[dict]:
        """Get price history for a route."""
        with self.session() as sess:
            route = sess.scalar(select(Route).where(
                Route.origin == origin.upper(),
                Route.destination == destination.upper(),
            ))
            if route is None:
                return []
            
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(
                Flight.departure_datetime,
                func.min(Flight.price_cents).label("min_price"),
                func.max(Flight.price_cents).label("max_price"),
                func.avg(Flight.price_cents).label("avg_price"),
            ).where(
                Flight.route_id == route.id,
                Flight.created_at >= cutoff,
            ).group_by(Flight.departure_datetime)
            
            results = sess.execute(stmt).fetchall()
            return [
                {
                    "date": r.departure_datetime.isoformat() if r.departure_datetime else None,
                    "min_price": r.min_price,
                    "max_price": r.max_price,
                    "avg_price": r.avg_price,
                }
                for r in results
            ]
    
    def get_config(self, key: str) -> Optional[str]:
        """Get a config value."""
        with self.session() as sess:
            value = sess.scalar(select(ConfigValue).where(ConfigValue.key == key))
            return value.value if value else None
    
    def set_config(self, key: str, value: str, description: Optional[str] = None) -> None:
        """Set a config value."""
        with self.session() as sess:
            config = sess.scalar(select(ConfigValue).where(ConfigValue.key == key))
            if config:
                config.value = value
                if description:
                    config.description = description
            else:
                config = ConfigValue(key=key, value=value, description=description)
                sess.add(config)
    
    def get_active_routes(self) -> list[Route]:
        """Get all active routes."""
        with self.session() as sess:
            stmt = select(Route).where(Route.is_active == True)
            return list(sess.execute(stmt).scalars().all())
    
    def close(self) -> None:
        """Close the database connection."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


_db_instance: Optional[Database] = None


def get_db(db_path: Optional[str] = None, echo: bool = False) -> Database:
    """Get or create a database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path=db_path, echo=echo)
    return _db_instance