# Flight Analysis

[![PyPI Version](https://img.shields.io/pypi/v/google-flight-analysis)](https://pypi.org/project/google-flight-analysis/)
[![Python Versions](https://img.shields.io/pypi/pyversions/google-flight-analysis)](https://pypi.org/project/google-flight-analysis/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/celebi-pkg/flight-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/celebi-pkg/flight-analysis/actions)

A Python package for scraping flight data from Google Flights and analyzing flight prices.

## Features

- **Scrape flight data** from Google Flights (round-trip, one-way, multi-city)
- **Store in SQLite** database for historical analysis
- **CLI interface** for agents and automation
- **Price history** tracking and analysis
- **Scheduled scraping** via GitHub Actions

## Installation

```bash
pip install google-flight-analysis
```

Or for development:

```bash
git clone https://github.com/celebi-pkg/flight-analysis
cd flight-analysis
pip install -e .
```

## Requirements

- Python 3.8+
- Chrome/Chromium browser
- ChromeDriver (auto-installed)

## Quick Start

### CLI Usage

```bash
# Get current price for a route
flight-cli price JFK LAX -d 2026-06-01

# Scrape and store flight data
flight-cli scrape JFK LAX -d 2026-06-01

# Database operations
flight-cli db init
flight-cli db routes
flight-cli db history JFK LAX --days 30
```

### Python API

```python
from google_flight_analysis import scrape, get_db

# Scrape flights
result = scrape("JFK", "LAX", "2026-06-01")
print(result.data)  # pandas DataFrame

# Save to database
result.save_to_db()

# Query price history
db = get_db()
history = db.get_price_history("JFK", "LAX", days=30)
```

### Available Commands

| Command | Description |
|---------|-------------|
| `price` | Get current flight prices |
| `scrape` | Scrape and store flight data |
| `db` | Database operations (init, info, routes, history) |
| `analyze` | Analyze prices, find best buy day |
| `recommend` | Recommend best flight option |

### Options

- `--json` - JSON output for agents
- `--date`, `-d` - Departure date (YYYY-MM-DD)
- `--return-date`, `-r` - Return date for round-trip
- `--trip-type` - one-way or round-trip

## Configuration

Configuration is managed via environment variables or Python:

```python
from google_flight_analysis import config

config.chrome.wait = 15  # seconds
config.db.path = "/path/to/flights.db"
```

Environment variables:
- `FLIGHT_DB_PATH` - Database path
- `FLIGHT_CACHE_DIR` - Cache directory

## Architecture

```
google_flight_analysis/
├── scrape/          # Scraping logic
│   ├── driver.py    # ChromeDriver wrapper
│   └── scrape.py   # Scrape class
├── db/             # Database
│   ├── models.py   # SQLAlchemy models
│   └── database.py # Database class
├── cli/             # CLI interface
├── legacy/          # Legacy components (fallback)
└── config.py       # Configuration
```

## Testing

```bash
pytest tests/ -v
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a PR

## License

MIT License - see LICENSE file.