'''/****************************************************************************************************************************************************************
  Written by Kaya Celebi, April 2023
****************************************************************************************************************************************************************/'''

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
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
		if len(args) <= 4:
			# base call protocol
			self._set_properties(*args)
			self._data = self._scrape_data()
			obj = self.clone(*args)
			obj.data = self._data
			return obj
		else:
			# data file being added to new scrape
			self._set_properties(*(args[:-1]))
			obj = self.clone(*(args[:-1]))
			obj.data = args[-1]
			return obj

	def __str__(self):
		if self._date_return is None:
			return "{dl}: {org} --> {dest}".format(
			dl = self._date_leave,
			org = self._origin,
			dest = self._dest
		)
		else:
			return "{dl}: {org} --> {dest}\n{dr}: {dest} --> {org}".format(
				dl = self._date_leave,
				dr = self._date_return,
				org = self._origin,
				dest = self._dest
			)

	def __repr__(self):
		if self._date_return is None:
			return "{n} RESULTS FOR:\n{dl}: {org} --> {dest}".format(
				n = self._data.shape[0],
				dl = self._date_leave,
				org = self._origin,
				dest = self._dest
			)
		else:
			return "{n} RESULTS FOR:\n{dl}: {org} --> {dest}\n{dr}: {dest} --> {org}".format(
				n = self._data.shape[0],
				dl = self._date_leave,
				dr = self._date_return,
				org = self._origin,
				dest = self._dest
			)

	def clone(self, *args):
		obj = _Scrape()
		obj._set_properties(*args)
		return obj

	'''
		Set properties upon scraper called.
	'''
	def _set_properties(self, *args):
		(
			self._origin, self._dest, self._date_leave, self._date_return
		) = args if len(args) >= 4 else (args + (None,))

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
		driver = webdriver.Chrome()#'/Users/kayacelebi/Downloads/chromedriver')
		driver.maximize_window()
		leave_result = self._get_results(self._make_url(self._date_leave, leave = True), driver)
		if self._date_return is not None:
			return_result = self._get_results(self._make_url(self._date_return, leave = False), driver)
			driver.quit()
			return pd.concat([leave_result, return_result], ignore_index = True)

		driver.quit()
		return leave_result


	def _make_url(self, date, leave = True):
		if leave:
			return 'https://www.google.com/travel/flights?q=Flights%20to%20{dest}%20from%20{org}%20on%20{date}%20oneway'.format(
				dest = self._dest,
				org = self._origin,
				date = date
			)
		else:
			return 'https://www.google.com/travel/flights?q=Flights%20to%20{org}%20from%20{dest}%20on%20{date}%20oneway'.format(
				dest = self._dest,
				org = self._origin,
				date = date
			)

	def _get_results(self, url, driver):
		results = None
		try:
			results = _Scrape._make_url_request(url, driver)
		except TimeoutException:
			print(
				'''TimeoutException, try again and check your internet connection!\n
				Also possible that no flights exist for your query :('''.replace('\t','')
			)
			return -1

		flights = self._clean_results(results)
		return Flight.dataframe(flights)

	def _clean_results(self, result):
		res2 = [x.encode("ascii", "ignore").decode().strip() for x in result]

		start = res2.index("Sort by:")+1
		mid_start = res2.index("Price insights")
		mid_end = -1
		try:
		    mid_end = res2.index("Other departing flights")+1
		except:
		    mid_end = res2.index("Other flights")+1
		end  = [i for i, x in enumerate(res2) if x.endswith('more flights')][0]

		res3 = res2[start:mid_start] + res2[mid_end:end]

		matches = [i for i, x in enumerate(res3) if len(x) > 2 and ((x[-2] != '+' and (x.endswith('PM') or x.endswith('AM'))) or x[-2] == '+')][::2]

		#matches = [i for i, x in enumerate(res3) if x.endswith('PM') or x.endswith('AM')][::2]

		flights = [Flight(self._date_leave, res3[matches[i]:matches[i+1]]) for i in range(len(matches)-1)]

		return flights

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
	def _make_url_request(url, driver):
		#driver = webdriver.Chrome()#'/Users/kayacelebi/Downloads/chromedriver')
		#driver.maximize_window()
		driver.get(url)

		# Waiting and initial XPATH cleaning
		WebDriverWait(driver, timeout = 10).until(lambda d: len(_Scrape._get_flight_elements(d)) > 100)
		results = _Scrape._get_flight_elements(driver)

		#driver.quit()

		return results

	@staticmethod
	def _get_flight_elements(driver):
		return driver.find_element(by = By.XPATH, value = '//body[@id = "yDmH0d"]').text.split('\n')

Scrape = _Scrape()