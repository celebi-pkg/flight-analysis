'''/****************************************************************************************************************************************************************
  Written by Kaya Celebi, April 2023
****************************************************************************************************************************************************************/'''

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from tqdm import tqdm

__all__ = ['Scrape', '_Scrape']

class _Scrape:

	def __init__(self):
		self._origin = None
		self._dest = None
		self._date_leave = None
		self._date_return = None
		self._data = None

	def __call__(self, *args):
		if len(args) == 4:
			self._set_properties(*args)
			self._data = self._scrape_data()
			obj = self.clone()
			obj.data = self._data
			return obj
		else:
			self._set_properties(*(args[:-1]))
			obj = self.clone()
			obj.data = args[-1]
			return obj

	def __str__(self):
		return "{dl}: {org} --> {dest}\n{dr}: {dest} --> {org}".format(
			dl = self._date_leave,
			dr = self._date_return,
			org = self._origin,
			dest = self._dest
		)

	def __repr__(self):
		return "{n} RESULTS FOR:\n{dl}: {org} --> {dest}\n{dr}: {dest} --> {org}".format(
			n = self._data.shape[0],
			dl = self._date_leave,
			dr = self._date_return,
			org = self._origin,
			dest = self._dest
		)

	def clone(self):
		obj = _Scrape()
		obj._set_properties(
			self._origin, self._dest, self._date_leave, self._date_return
		)
		return obj

	'''
		Set properties upon scraper called.
	'''
	def _set_properties(self, *args):
		(
			self._origin, self._dest, self._date_leave, self._date_return
		) = args

	@property
	def origin(self):
		return self._origin

	@origin.setter
	def origin(self, x : str) -> None:
		self._origin = x

	@property
	def dest(self):
		return self._dest

	@dest.setter
	def dest(self, x : str) -> None:
		self._dest = x

	@property
	def date_leave(self):
		return self._date_leave

	@date_leave.setter
	def date_leave(self, x : str) -> None:
		self._date_leave = x

	@property
	def date_return(self):
		return self._date_return

	@date_return.setter
	def date_return(self, x : str) -> None:
		self._date_return = x

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, x):
		self._data = x

	'''
		Scrape the object
	'''
	def _scrape_data(self):
		url = self._make_url()
		return self._get_results(url)


	def _make_url(self):
		return 'https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{org}%20on%20{dl}%20through%20{dr}'.format(
			dest = self._dest,
			org = self._origin,
			dl = self._date_leave,
			dr = self._date_return
		)

	def _get_results(self, url):
		results = _Scrape._make_url_request(url)

		flight_info = _Scrape._get_info(results)
		partition = _Scrape._partition_info(flight_info)

		return _Scrape._parse_columns(partition, self._date_leave, self._date_return)

	@staticmethod
	def _get_driver():
		driver = None
		try:
			driver = webdriver.Chrome()
		except:
			raise Exception(
				'''Appropriate ChromeDriver version not found.\n
				Make sure Chromedriver is downloaded with appropriate version of Chrome.\n
				In Chrome, Go to Settings --> About Chrome to find version.\n 
				Visit https://chromedriver.chromium.org and download matching ChromeDriver version.
				'''
			)

	@staticmethod
	def _make_url_request(url):
		driver = webdriver.Chrome()#'/Users/kayacelebi/Downloads/chromedriver')
		driver.get(url)

		# Waiting and initial XPATH cleaning
		WebDriverWait(driver, timeout = 10).until(lambda d: len(_Scrape._get_flight_elements(d)) > 100)
		results = _Scrape._get_flight_elements(driver)

		driver.quit()

		return results

	@staticmethod
	def _get_flight_elements(driver):
		return driver.find_element(by = By.XPATH, value = '//body[@id = "yDmH0d"]').text.split('\n')

	@staticmethod
	def _get_info(result):
		info = []
		collect = False
		for r in result:
			if 'more flights' in r:
				collect = False

			if collect and 'price' not in r.lower() and 'prices' not in r.lower() and 'other' not in r.lower() and ' – ' not in r.lower():
				info += [r]

			if r == 'Sort by:':
				collect = True

		return info

	@staticmethod
	def _partition_info(info):
		i, grouped = 0, []
		while i < len(info) - 1:
			j = i + 2
			end = -1
			while j < len(info):
				if _Scrape._end_condition(info[j]):
					end = j
					break
				j += 1

			if end == -1:
				break
			grouped += [info[i:end]]
			i = end

		return grouped

	@staticmethod
	def _end_condition(x):
		if len(x) < 2:
			return False

		if x[-2] == "+":
			x = x[:-2]

		if x[-2:] == 'AM' or x[-2:] == 'PM':
			return True
		return False

	@staticmethod
	def _parse_columns(grouped, date_leave, date_return):
		# Instantiate empty column arrays
		depart_time = []
		arrival_time = []
		airline = []
		travel_time = []
		origin = []
		dest = []
		stops = []
		stop_time = []
		stop_location = []
		co2_emission = []
		emission = []
		price = []
		trip_type = []
		access_date = [date.today().strftime('%Y-%m-%d')]*len(grouped)

		# For each "flight"
		for g in grouped:
			i_diff = 0 # int that checks if we need to jump ahead based on some conditions

			# Get departure and arrival times
			depart_time += [g[0]]
			arrival_time += [g[1]]

			# When this string shows up we jump ahead an index
			i_diff += 1 if 'Separate tickets booked together' in g[2] else 0

			# Add airline, travel time, origin, and dest
			airline += [g[2 + i_diff]]
			travel_time += [g[3 + i_diff]]
			origin += [g[4 + i_diff].split('–')[0]]
			dest += [g[4 + i_diff].split('–')[1]]

			# Grab the number of stops by splitting string
			num_stops = 0 if 'Nonstop' in g[5 + i_diff] else int(g[5 + i_diff].split('stop')[0])
			stops += [num_stops]

			# Add stop time/location given whether its nonstop flight or not
			stop_time += [None if num_stops == 0 else (g[6 + i_diff].split('min')[0] if num_stops == 1 else None)]
			stop_location += [None if num_stops == 0 else (g[6 + i_diff].split('min')[1] if num_stops == 1 and 'min' in g[6 + i_diff] else [g[6 + i_diff].split('hr')[1] if 'hr' in g[6 + i_diff] and num_stops == 1 else g[6 + i_diff]])]

			# Jump ahead an index if flight isn't nonstop to accomodate for stop_time, stop_location
			i_diff += 0 if num_stops == 0 else 1

			# If Co2 emission not listed then we skip, else we add
			if g[6 + i_diff] != '–':
				co2_emission += [float(g[6 + i_diff].replace(',','').split(' kg')[0])]
				emission += [0 if g[7 + i_diff] == 'Avg emissions' else int(g[7 + i_diff].split('%')[0])]

				price += [float(g[8 + i_diff][1:].replace(',',''))]
				trip_type += [g[9 + i_diff]]
			else:
				co2_emission += [None]
				emission += [None]
				price += [float(g[7 + i_diff][1:].replace(',',''))]
				trip_type += [g[8 + i_diff]]


		return pd.DataFrame({
			'Leave Date' : [date_leave]*len(grouped),
			'Return Date' : [date_return]*len(grouped),
			'Depart Time (Leg 1)' : depart_time,
			'Arrival Time (Leg 1)' : arrival_time,
			'Airline(s)' : airline,
			'Travel Time' : travel_time,
			'Origin' : origin,
			'Destination' : dest,
			'Num Stops' : stops,
			'Layover Time' : stop_time,
			'Stop Location' : stop_location,
			'CO2 Emission' : co2_emission,
			'Emission Avg Diff (%)' : emission,
			'Price ($)' : price,
			'Trip Type' : trip_type,
			'Access Date' : access_date
		})

Scrape = _Scrape()