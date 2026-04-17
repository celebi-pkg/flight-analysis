# Flight Analysis - Master Scoping Document

**Version**: 1.0  
**Date**: 2026-04-17  
**Status**: Active Revival Project

---

## 1. Project Overview

### What This Project Is

**google-flight-analysis** is a Python package for scraping flight data from Google Flights and analyzing/forecasting flight prices. Originally published to PyPI (v1.2.0), it's designed to:

- Scrape real-time flight prices from Google Flights
- Store scraped data in SQLite or CSV
- Support multiple trip types: one-way, round-trip, chain-trip, perfect-chain
- Eventually include ML models for price forecasting

### Current State

**Functionality**: Semi-working. The scraping infrastructure exists but is fragile due to:
- Hardcoded XPath selectors that break when Google updates the UI
- Deprecated code in `scrape/deprc/` that was the main implementation
- No actual DB setup or cron jobs
- Tests are mostly broken/commented out

**PyPI Status**: Published (v1.2.0) but outdated

---

## 2. Current Implementation

### Directory Structure

```
flight-analysis/
├── src/google_flight_analysis/
│   ├── config/config.py          # ChromeDriver & scraping instruction configs
│   ├── scrape/
│   │   ├── chrome_wrapper.py     # Selenium wrapper with instruction engine
│   │   ├── scrape.py            # New scrape function (minimal)
│   │   ├── route.py             # Stub for Route classes
│   │   ├── flight.py           # (deprecated, in deprc/)
│   │   └── deprc/               # Deprecated implementations
│   │       ├── scrape.py        # Main Scrape class - MOST COMPLETE
│   │       └── flight.py        # Flight parsing
│   ├── cache/
│   │   └── cache.py            # SQLite/CSV caching
│   └── analyze/
│       └── analysis.py         # Stub - minimal
├── tests/
│   └── test_class.py         # Broken tests
├── .github/workflows/        # CI/CD (publish only, no tests)
├── setup.cfg                # Package config
├── pyproject.toml          # Build config
└── README.md              # Documentation
```

### What's Implemented

| Component | Status | Details |
|-----------|--------|---------|
| **ChromeDriverWrapper** | ✅ Working | Selenium with batch instruction engine |
| **Config System** | ✅ Working |instruction batches in config.py |
| **_Scrape Class** | ⚠️ Partial | Trip type handling in deprc/, broken scraping |
| **Route Classes** | ❌ Stub | Empty classes in route.py |
| **Cache/SQL** | ⚠️ Fragmented | Partial SQLite support, broken |
| **Analysis/ML** | ❌ None | Empty stubs |
| **Test Suite** | ❌ Broken | Most tests commented out |
| **CI/CD** | ⚠️ Minimal | Only publish workflows |

### Key Code Locations

- **Main Scrape logic**: `src/google_flight_analysis/scrape/deprc/scrape.py`
- **ChromeWrapper**: `src/google_flight_analysis/scrape/chrome_wrapper.py:16-98`
- **Config**: `src/google_flight_analysis/config/config.py:47-211`
- **Flight parsing**: `src/google_flight_analysis/scrape/deprc/flight.py`

---

## 3. Branch Comparison

### Branch: `restructure-a0` (Current)

**vs main**: Changes on this branch represent a restructuring effort:

| Change | File(s) | Impact |
|--------|---------|--------|
| Created `src/google_flight_analysis/config/` | New | Centralized config |
| Restructured `scrape/` modules | New | Separated concerns |
| Added ChromeWrapper | New | New scraping engine |
| Deprecated old code | To `deprc/` | Cleanup in progress |
| Config has updated instructions | config.py | Better XPath queries |
| Tests stripped down | test_class.py | Broken/incomplete |

### What's Different From Main

1. **New extraction approach**: Instruction-based extraction via `ChromeDriverWrapper.instructions()` instead of raw text parsing
2. **Config-driven**: All scraping instructions in `config.py` now
3. **Incomplete migration**: Old code in `deprc/` uses different approach
4. **No working scraping**: Current branch has no end-to-end working scrape

### Files Modified On This Branch

```bash
modified:   src/google_flight_analysis/config/config.py
modified:   src/google_flight_analysis/scrape/chrome_wrapper.py
modified:   src/google_flight_analysis/scrape/scrape.py
modified:   tests/test_class.py
```

---

## 4. Revival Requirements

### Phase 1: Database & Cron Infrastructure

**Priority: HIGH**

- [ ] Setup SQLite database schema for flight data
- [ ] Create database migrations (use Alembic or simple SQL)
- [ ] Add GitHub Actions cron job for scheduled scraping
- [ ] Define scrapable routes (popular routes from user input)
- [ ] Implement rate limiting and retry logic
- [ ] Set up data retention policies

### Phase 2: Testing Suite

**Priority: HIGH**

- [ ] Fix/rewrite test_class.py with real unit tests
- [ ] Add tests for scraping (mocked/puppeteer)
- [ ] Add tests for data transformations
- [ ] Integrate test CI on ALL commits (not just publish)
- [ ] Add linting (ruff or flake8)
- [ ] Add type checking (mypy)
- [ ] Set up pre-commit hooks

### Phase 3: CLI for Agents

**Priority: HIGH**

- [ ] Design CLI interface (Click or argparse)
- [ ] Command: `flight price <origin> <dest> <date>` - Get current price
- [ ] Command: `flight scrape <route>` - Scrape and store
- [ ] Command: `flight db` - Database operations
- [ ] Command: `flight analyze` - ML inference
- [ ] Command: `flight recommend` - Best day to buy
- [ ] Add agent-friendly JSON output option
- [ ] Add config file support

### Phase 4: ML/Analysis

**Priority: MEDIUM**

- [ ] Implement price history analysis
- [ ] Create simple forecasting models
- [ ] Add "best day to buy" algorithm
- [ ] Document model approach
- [ ] Add inference CLI command
- [ ] Add model versioning

### Phase 5: Polish & Release

**Priority: MEDIUM**

- [ ] Update README with current usage
- [ ] Add proper documentation
- [ ] Fix PyPI release pipeline
- [ ] Version bump (v2.0.0)
- [ ] Add badges for tests/CI

---

## 5. Technical Decisions Needed

### Database

- **Recommended**: SQLite for local, PostgreSQL for production
- **Migration tool**: Alembic or homemade
- **Consider**: SQLite + SQLAlchemy for now

### Testing Framework

- **pytest** is already used but broken
- Need: Mock chrome driver or use recorded responses

### CLI Framework

- **Click** recommended (better for agents)
- Alternative: argparse (stdlib)

### Scraping Approach

Current option in config:
- **Instruction-based**: Batches of (method, xpath) pairs
- **Pros**: Configurable, less code changes
- **Cons**: Fragile if selectors change

---

## 6. Dependencies

Current (`setup.cfg`):
- tqdm
- numpy
- pandas
- selenium
- sqlalchemy
- chromedriver-autoinstaller (runtime)

To add:
- click (CLI)
- pytest (testing)
- ruff (linting)
- mypy (types)
- python-dotenv (config)

---

## 7. Known Issues

1. **XPath selectors break**: Google's UI changes break scrapers
2. **No data persistence**: DB exists but incomplete
3. **No ML**: Analysis stubs are empty
4. **Tests don't run**: CI doesn't run tests
5. **No scheduling**: No cron job exists

---

## 8. Action Items (Immediate)

- [ ] Run existing tests to see failures
- [ ] Verify ChromeDriver can reach Google Flights
- [ ] Define first set of routes to scrape
- [ ] Design DB schema
- [ ] Write working Scrape class

---

*This is the master document. All tasks should be tracked via this file or linked from it.*