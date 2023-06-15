'''/****************************************************************************************************************************************************************
  Written by Kaya Celebi, April 2023
****************************************************************************************************************************************************************/'''

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from tqdm import tqdm

from google_flight_analysis.flight import *

__all__ = ['Scrape', '_Scrape', 'ScrapeObjects']

date_format = "%Y-%m-%d"
'''
	Iterative scraping
	If value in DB dont run just return query
	Scraping object overhaul
	argument change
	advanced filters
	Europe date display vs US date display!
'''

def ScrapeObjects(objs, deep_copy = False):
	if type(objs) is _Scrape:
		objs = [objs]


	chromedriver_autoinstaller.install() # check if chromedriver is installed correctly and on path
	driver = webdriver.Chrome()
	driver.maximize_window()

	# modifies the objects in-place
	debug = [obj._scrape_data(driver) for obj in tqdm(objs, desc="Scraping Objects")]
	
	driver.quit()

	if deep_copy:
		return objs # returns objs as copy

class _Scrape:

	def __init__(self):
		self._origin = None
		self._dest = None
		self._date = None
		self._data = pd.DataFrame()
		self._url = None
		self._type = None

	# if date leave and date return, return 2 objects?
	def __call__(self, *args):
		# base call protocol
		self._set_properties(*args)
		obj = self.clone(*args)
		obj.data = self._data
		return obj


	# Ability to combine a going and return trip
	# Can use this to chain multiple trips
	def __add__(self, other):

		assert self.type == other.type, "Can't add {a} with {b}. See docs".format(a = self.type, b = other.type)

		assert (self.data.empty and other.data.empty) or (not self.data.empty and not other.data.empty), "Error with addition. Both queries must either be unused or queried."

		obj_type = self.type
		if obj_type == 'one-way':
			# adding two one-ways could be a round trip
			if self.origin == other.dest and self.dest == other.origin:

				if self.data.empty:
					return Scrape(self.origin[0], self.dest[0], *self.date, *other.date)
				else:
					obj = Scrape(self.origin[0], self.dest[0], *self.date)
					obj.data = pd.concat([self.data, other.data])
					return obj

			# otherwise, must be chain
			if self.data.empty:
				return Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
			else:
				obj = Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
				obj.data = pd.concat([self.data, other.data])
				return obj


		elif obj_type == 'round-trip':
			# adding two round-trips makes it into a chain, possible perfect chain
			# example of perfect: (JFK --> IST, IST --> JFK) + (JFK --> CDG, CDG --> JFK)

			assert datetime.strptime(self.date[1], date_format) < datetime.strptime(other.date[0], date_format), "Dates are not in order. Make sure to provide them in increasing order in YYYY-MM-DD format."

			# check perfect chain
			if self.origin[0] == other.origin[0]:
				if self.data.empty:
					return Scrape(
						*self.unpack([[self.origin[i], date] for i, date in enumerate(self.date)]),
						*self.unpack([[other.origin[i], date] for i, date in enumerate(other.date)] + [[other.dest[-1]]])
					)
				else:
					obj = Scrape(
						*self.unpack([[self.origin[i], date] for i, date in enumerate(self.date)]),
						*self.unpack([[other.origin[i], date] for i, date in enumerate(other.date)] + [[other.dest[-1]]])
					)
					obj.data = pd.concat([self.data, other.data])
					return obj

			# otherwise, return chain
			if self.data.empty:
				return Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
			else:
				obj = Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
				obj.data = pd.concat([self.data, other.data])
				return obj

		elif obj_type == 'chain-trip':
			# must result in chain
			# check last date of self < first of other

			assert datetime.strptime(self.date[-1], date_format) < datetime.strptime(other.date[0], date_format), "Dates are not in order. Make sure to provide them in increasing order in YYYY-MM-DD format."

			if self.data.empty:
				return Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
			else:
				obj = Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
				obj.data = pd.concat([self.data, other.data])
				return obj

		elif obj_type == 'perfect-chain':
			# only outputs perfect chain if origins are same

			assert datetime.strptime(self.date[-1], date_format) < datetime.strptime(other.date[0], date_format), "Dates are not in order. Make sure to provide them in increasing order in YYYY-MM-DD format."

			# perfect-chain
			if self.origin[0] == other.origin[0]:

				if self.data.empty:
					return Scrape(
						*self.unpack([[self.origin[i], date] for i, date in enumerate(self.date)]),
						*self.unpack([[other.origin[i], date] for i, date in enumerate(other.date)] + [[other.dest[-1]]])
					)
				else:
					obj = Scrape(
						*self.unpack([[self.origin[i], date] for i, date in enumerate(self.date)]),
						*self.unpack([[other.origin[i], date] for i, date in enumerate(other.date)] + [[other.dest[-1]]])
					)
					obj.data = pd.concat([self.data, other.data])
					return obj

			# otherwise, just chain
			if self.data.empty:
				return Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
			else:
				obj = Scrape(
					*self.unpack([[self.origin[i], self.dest[i], date] for i, date in enumerate(self.date)]),
					*self.unpack([[other.origin[i], other.dest[i], date] for i, date in enumerate(other.date)])
				)
				obj.data = pd.concat([self.data, other.data])
				return obj

		else:
			raise NotImplementedError()

	
	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		rep = "Scrape( "

		if self._data.shape[0] == 0:
			rep += "{Query Not Yet Used}\n"
		else:
			rep += "{n} RESULTS FOR:\n".format(n = self._data.shape[0])

		for i, date in enumerate(self._date):
			rep += "{d}: {org} --> {dest}\n".format(
				d = date,
				org = self._origin[i],
				dest = self._dest[i]
			)
		
		rep += ")"

		return rep

	def clone(self, *args):
		obj = _Scrape()
		obj._set_properties(*args)
		return obj

	def unpack(self, args):
		arr = []
		for arg in args:
			arr += arg
		return arr

	def combine(self, other, *args):
		if self.data is None:
			return Scrape(*args)
		
		obj = Scrape(*args)
		obj.data = pd.concat([self.data, other.data])
		return obj

	'''
		Set properties upon scraper called.
	'''
	def _set_properties(self, *args):
		'''
			args Format

			one-way:
				org, dest, date

			round-trip:
				org, dest, dateleave, datereturn

			chain-trip:
				org, dest, date, org, dest, date, org, dest, date ...

			perfect-chain:
				org, date, org, date, org, date, org, date, ..., dest
				implied condition: dest of prev city = origin of next city
		'''

		# one way
		if len(args) == 3:
			assert len(args[0]) == 3 and type(args[0]) == str, "Issue with arg 0, see docs"
			assert len(args[1]) == 3 and type(args[1]) == str, "Issue with arg 1, see docs"
			assert len(args[2]) == 10 and type(args[2]) == str, "Issue with arg 2, see docs"

			self._origin, self._dest, self._date = [args[0]], [args[1]], [args[2]]

			#assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
			self._url = self._make_url()
			self._type = 'one-way'

		# round-trip
		elif len(args) == 4:
			assert len(args[0]) == 3 and type(args[0]) == str, "Issue with arg 0, see docs"
			assert len(args[1]) == 3 and type(args[1]) == str, "Issue with arg 1, see docs"
			assert len(args[2]) == 10 and type(args[2]) == str, "Issue with arg 2, see docs"
			assert len(args[3]) == 10 and type(args[3]) == str, "Issue with arg 3, see docs"

			assert datetime.strptime(args[2], date_format) < datetime.strptime(args[3], date_format), "Dates are not in order. Make sure to provide them in increasing order in YYYY-MM-DD format."

			self._origin, self._dest, self._date = [args[0], args[1]], [args[1], args[0]], args[2:]

			assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
			self._url = self._make_url()
			self._type = 'round-trip'

		# chain-trip, chain is component of 3s, check that last one is an actual date to not confuse w perfect
		elif len(args) >= 3 and len(args) % 3 == 0 and len(args[-1]) == 10 and type(args[-1]) == str:
			self._origin, self._dest, self._date = [], [], []

			for i in range(0, len(args), 3):
				assert len(args[i]) == 3 and type(args[i]) == str, "Issue with arg {}, see docs".format(i)
				assert len(args[i + 1]) == 3 and type(args[i+1]) == str, "Issue with arg {}, see docs".format(i+1)
				assert len(args[i + 2]) == 10 and type(args[i + 2]) == str, "Issue with arg {}, see docs".format(i+2)
				
				if i > 0:
					assert datetime.strptime(self._date[-1], date_format) < datetime.strptime(args[i + 2], date_format), "Dates are not in order ({d1} > {d2}). Make sure to provide them in increasing order in YYYY-MM-DD format.".format(d1 = self._date[-1], d2 = args[i+2])

				self._origin += [args[i]]
				self._dest += [args[i + 1]]
				self._date += [args[i + 2]]

			assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
			self._url = self._make_url()
			self._type = 'chain-trip'


		# perfect-chain
		elif len(args) >= 4 and len(args) % 2 == 1 and len(args[-1]) == 3 and type(args[-1]) == str:
			assert len(args[0]) == 3 and type(args[0]) == str, "Issue with arg 0, see docs"
			assert len(args[1]) == 10 and type(args[1]) == str, "Issue with arg 1, see docs"

			self._origin, self._dest, self._date = [args[0]], [], [args[1]]

			for i in range(2, len(args)-1, 2):
				assert len(args[i]) == 3 and type(args[i]) == str, "Issue with arg {}, see docs".format(i)
				assert len(args[i + 1]) == 10 and type(args[i + 1]) == str, "Issue with arg {}, see docs".format(i+1)
				assert datetime.strptime(self._date[-1], date_format) < datetime.strptime(args[i + 1], date_format), "Dates are not in order ({d1} > {d2}). Make sure to provide them in increasing order in YYYY-MM-DD format.".format(d1 = self._date[-1], d2 = args[i+1])

				self._origin += [args[i]]
				self._dest += [args[i]]
				self._date += [args[i+1]]

			assert len(args[-1]) == 3 and type(args[-1]) == str, "Issue with last arg, see docs"
			self._dest += [args[-1]]

			assert len(self._origin) == len(self._dest) == len(self._date), "Issue with array lengths, talk to dev"
			self._url = self._make_url()
			self._type = 'perfect-chain'

		else:
			raise NotImplementedError()

	@property
	def origin(self):
		return self._origin

	@origin.setter
	def origin(self, x : str) -> None:
		assert self._data.shape[0] == 0, "Can't set origin after query has been completed."
		self._origin = x

	@property
	def dest(self):
		return self._dest

	@dest.setter
	def dest(self, x : str) -> None:
		assert self._data.shape[0] == 0, "Can't set destination after query has been completed."
		self._dest = x

	@property
	def date(self):
		return self._date

	@date.setter
	def date(self, x : str) -> None:
		assert self._data.shape[0] == 0, "Can't set date after query has been completed."
		self.date = x

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, x):
		self._data = x

	@property
	def url(self):
		return self._url

	@property
	def type(self):
		return self._type


	'''
		Scrape the object. Add support for multiple queries, iterative.
	'''
	def _scrape_data(self, driver):
		results = [self._get_results(url, self._date[i], driver) for i, url in enumerate(self._url)]
		self._data = pd.concat(results, ignore_index = True)


	def _make_url(self):
		urls = []
		for i in range(len(self._date)):
			urls += [
				'https://www.google.com/travel/flights?hl=en&q=Flights%20to%20{org}%20from%20{dest}%20on%20{date}%20oneway'.format(
					dest = self._dest[i],
					org = self._origin[i],
					date = self._date[i]
				)
			]
		return urls

	@staticmethod
	def _get_results(url, date, driver):
		results = None
		try:
			results = _Scrape._make_url_request(url, driver)
		except TimeoutException:
			print(
				'''TimeoutException, try again and check your internet connection!\n
				Also possible that no flights exist for your query :('''.replace('\t','')
			)
			return -1

		flights = _Scrape._clean_results(results, date)
		return Flight.dataframe(flights)

	@staticmethod
	def _clean_results(result, date):
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

		matches = [i for i, x in enumerate(res3) if len(x) > 2 and ((x[-2] != '+' and (x.endswith('PM') or x.endswith('AM')) and ':' in x) or x[-2] == '+')][::2]
		flights = [Flight(date, res3[matches[i]:matches[i+1]]) for i in range(len(matches)-1)]

		return flights

	@staticmethod
	def _make_url_request(url, driver):
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