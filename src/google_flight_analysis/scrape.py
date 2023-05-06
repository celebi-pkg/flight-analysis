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

import sys
sys.path.append('src/google_flight_analysis')
from flight import *

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
			# base call protocol
			self._set_properties(*args)
			self._data = self._scrape_data()
			obj = self.clone()
			obj.data = self._data
			return obj
		else:
			# data file being added to new scrape
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

		res2 = [x.encode("ascii", "ignore").decode().strip() for x in res1]

		start = res2.index("Sort by:")+1
		mid_start = res2.index("Price insights")
		mid_end = res2.index("Other departing flights")+1
		end  = [i for i, x in enumerate(res2) if x.endswith('more flights')][0]

		res3 = res2[start:mid_start] + res2[mid_end:end]

		matches = [i for i, x in enumerate(res3) if x.endswith('PM') or x.endswith('AM')][::2]

		flights = [Flight(self._date_leave, self._date_return, res3[matches[i]:matches[i+1]]) for i in range(len(matches)-1)]

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
		driver.maximize_window()
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
	def _parse_columns(grouped, date_leave, date_return):


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