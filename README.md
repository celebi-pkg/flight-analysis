[![kcelebi](https://circleci.com/gh/celebi-pkg/flight-analysis.svg?style=svg)](https://circleci.com/gh/celebi-pkg/flight-analysis)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live on PyPI](https://img.shields.io/badge/PyPI-1.2.0-brightgreen)](https://pypi.org/project/google-flight-analysis/)
[![TestPyPI](https://img.shields.io/badge/PyPI-1.1.1--alpha.11-blue)](https://test.pypi.org/project/google-flight-analysis/1.1.1a11/)

# Flight Analysis

This project provides tools and models for users to analyze, forecast, and collect data regarding flights and prices. There are currently many features in initial stages and in development. The current features (as of 5/25/2023) are:

- Detailed scraping and querying tools for Google Flights
- Ability to store data locally or to SQL tables
- Base analytical tools/methods for price forecasting/summary

The features in development are:

- Models to demonstrate ML techniques on forecasting
- Querying of advanced features
- API for access to previously collected data

## Table of Contents
- [Overview](#Overview)
- [Usage](#usage)
- [Updates & New Features](#updates-&-new-features)
- [Real Usage](#real-usage) 😄


## Overview

Flight price calculation can either use newly scraped data (scrapes upon running it) or cached data that reports a price-change confidence determined by a trained model. Currently, many features of this application are in development.

## Usage

The web scraping tool is currently functional only for scraping round trip flights for a given origin, destination, and date range. It can be easily used in a script or a jupyter notebook.

Note that the following packages are **absolutely required** as dependencies:
- tqdm
- selenium **(make sure to update your [ChromeDriver](https://chromedriver.chromium.org)!)**
- pandas
- numpy

You can easily install this by running either installing the Python package `google-flight-analysis`:

	pip install google-flight-analysis

or forking/cloning this repository. Upon doing so, make sure to install the dependencies and update ChromeDriver to match your Google Chrome version.

	pip install -r requirements.txt


The main scraping function that makes up the backbone of most other functionalities is `Scrape()`. It serves also as a data object, preserving the flight information as well as meta-data from your query. For Python package users, import as follows:

	from google_flight_analysis.scrape import *

For GitHub repository cloners, import as follows from the root of the repository:

	from src.google_flight_analysis.scrape import *
	#---OR---#
	import sys
	sys.path.append('src/google_flight_analysis')
	from scrape import *


Here is some quick starter code to accomplish the basic tasks. Find more in the [documentation](https://kcelebi.github.io/flight-analysis/).

	# Keep the dates in format YYYY-mm-dd
	result = Scrape('JFK', 'IST', '2023-07-20', '2023-08-20') # obtain our scrape object, represents out query
	result.type # This is in a round-trip format
	result.origin # ['JFK', 'IST']
	result.dest # ['IST', 'JFK']
	result.dates # ['2023-07-20', '2023-08-20']
	print(result) # get unqueried str representation

A `Scrape` object represents a Google Flights query to be run. It maintains flights as a sequence of one or more one-way flights which have a origin, destination, and flight date. The above object for a round-trip flight from JFK to IST is a sequence of JFK --> IST, then IST --> JFK. We can obtain the data as follows:

	ScrapeObjects(result) # runs selenium through ChromeDriver, modifies results in-place
	result.data # returns pandas DF
	print(result) # get queried representation of result

You can also scrape for one-way trips:

	results = Scrape('JFK', 'IST', '2023-08-20')
	ScrapeObjects(result)
	result.data #see data

You can also scrape chain-trips, which are defined as a sequence of one-way flights that have no direct relation to each other, other than being in chronological order. 

	# chain-trip format: origin, dest, date, origin, dest, date, ...
	result = Scrape('JFK', 'IST', '2023-08-20', 'RDU', 'LGA', '2023-12-25', 'EWR', 'SFO', '2024-01-20')
	result.type # chain-trip
	ScrapeObjects(result)
	result.data # see data

You can also scrape perfect-chains, which are defined as a sequence of one-way flights such that the destination of the previous flight is the origin of the next and the origin of the chain is the final destination of the chain (a cycle).

	# perfect-chain format: origin, date, origin, date, ..., first_origin
	result = Scrape("JFK", "2023-09-20", "IST", "2023-09-25", "CDG", "2023-10-10", "LHR", "2023-11-01", "JFK")
	result.type # perfect-chain
	ScrapeObjects(result)
	result.data # see data

You can read more about the different type of trips in the documentation. Scrape objects can be added to one another to create larger queries. This is under the conditions:

1. The objects being added are the same type of trip (one-way, round-trip, etc)
2. The objects being added are either both unqueried or both queried

## Updates & New Features

Performing a complete revamp of this package, including new addition to PyPI. Documentation is being updated frequently, contact for any questions.


<!--
## Cache Data

The caching system for this application is mainly designed to make the loading of data more efficient. For the moment, this component of the application hasn't been designed well for the public to easily use so I would suggest that most people leave it alone, or fork the repository and modify some of the functions to create folders in the destinations that they would prefer. The key caching functions are:

- `cache_data`
- `load_cached`
- `iterative_caching`
- `clean_cache`
- `cache_condition`
- `check_cached`

All of these functions are clearly documented in the `scraping.py` file.
-->
<!--## To Do

- [x] Scrape data and clean it
- [x] Testing for scraping
- [x] Add scraping docs
- [ ] Split Airlines
- [ ] Add day of week as a feature
- [ ] Support for Day of booking!! ("Delayed by x hr")
- [ ] Detail most common airports and automatically cache
- [ ] Algorithm to check over multiple days and return summary
- [x] Determine caching method: wait for request and cache? periodically cache?
- [ ] Model for observing change in flight price
	- Predict how much it'll maybe change
- [ ] UI for showing flights that are 'perfect' to constraint / flights that are close to constraints, etc
- [ ] Caching/storing data, uses predictive model to estimate how good this is

-->
## Real Usage

Here are some great flights I was able to find and actually booked when planning my travel/vacations:

- NYC ➡️ AMS (May 9), AMS ➡️ IST (May 12), IST ➡️ NYC (May 23) | Trip Total: $611 as of March 7, 2022
