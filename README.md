[![kcelebi](https://circleci.com/gh/celebi-pkg/flight-analysis.svg?style=svg)](https://circleci.com/gh/celebi-pkg/flight-analysis)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Live on PyPI](https://img.shields.io/badge/PyPI-1.0.0-brightgreen)](https://pypi.org/project/google-flight-analysis/)

# Flight Analysis

This project provides tools and models for users to analyze, forecast, and collect data regarding flights and prices. There are currently many features in initial stages and in development. The current features (as of 4/5/2023) are:

- Scraping tools for Google Flights
- Base analytical tools/methods for price forecasting/summary

The features in development are:

- Models to demonstrate ML techniques on forecasting
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

	# Try to keep the dates in format YYYY-mm-dd
	result = Scrape('JFK', 'IST', '2023-07-20', '2023-08-10') # obtain our scrape object
	dataframe = result.data # outputs a Pandas DF with flight prices/info
	origin = result.origin # 'JFK'
	dest = result.dest # 'IST'
	date_leave = result.date_leave # '2023-05-20'
	date_return = result.date_return # '2023-06-10'

You can also scrape for one-way trips now:

	results = Scrape('JFK', 'IST', '2023-08-20')
	result.data.head() #see data


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
