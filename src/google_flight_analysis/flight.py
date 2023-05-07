from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from tqdm import tqdm

__all__ = ['Flight']


class Flight:

	def __init__(self, dl, *args):
		self._id = 1
		self._origin = None
		self._dest = None
		self._date = dl
		self._dow = datetime.strptime(dl, '%Y-%m-%d').isoweekday() # day of week
		self._airline = None
		self._flight_time = None
		self._num_stops = None
		self._stops = []
		self._co2 = None
		self._emissions = None
		self._price = None
		self._time_leave = None
		self._time_arrive = None

		self._parse_args(*args)

	def __repr__(self):
		...

	def __str__(self):
		...

	@property
	def id(self):
		return self._id

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
	def date(self):
		return self._date

	@date.setter
	def date(self, x : str) -> None:
		self._date = x

	@property
	def dow(self):
		return self._dow

	@property
	def airline(self):
		return self._airline

	@property
	def flight_time(self):
		return self._flight_time

	@property
	def num_stops(self):
		return self._num_stops

	@property
	def stops(self):
		return self._stops

	@property
	def co2(self):
		return self._co2

	@property
	def emissions(self):
		return self._emissions

	@property
	def price(self):
		return self._price

	@property
	def time_leave(self):
		return self._time_leave

	@property
	def time_arrive(self):
		return self._time_arrive
	


	def _parse_args(self, args):
		assert args[0].endswith('AM') or  args[0].endswith('PM'), Flight.assert_error(0)
		assert args[2].endswith('AM') or  args[2].endswith('PM'), Flight.assert_error(1)
		date_format = '%Y-%m-%d %I:%M%p'
		self._time_leave = datetime.strptime(self._date + " " + args[0], date_format)
		self._time_arrive = datetime.strptime(self._date + " " + args[2], date_format)

		# overnight flight
		if args[0].endswith('PM') and args[2].endswith('AM'):
			self._time_arrive += datetime.timedelta(days=1)

		self._airline = args[3].split('Operated')[0]
		self._flight_time = args[4]
		self._origin = args[5][:3]
		self._dest = args[5][3:]

		assert 'stop' in args[6], Flight.assert_error(6)
		self._num_stops = 0 if args[6] == 'Nonstop' else int(args[6].split()[0])

		if self._num_stops > 0:
			self._stops += args[7:7 + self._num_stops]

			assert args[7 + self._num_stops].endswith('CO2'), Flight.assert_error(7)
			self._co2 = int(args[7 + self._num_stops].split()[0])

			assert args[8 + self._num_stops].endswith('emissions'), Flight.assert_error(8)
			emission_val = args[8 + self._num_stops].split()[0]
			self._emissions = 0 if emission_val == 'Avg' else int(emission_val[:-1])

			assert args[9 + self._num_stops].startswith('$'), Flight.assert_error(9)
			self._price = int(args[9 + self._num_stops][1:])

		else:
			assert args[7].endswith('CO2'), Flight.assert_error(7)
			self._co2 = int(args[7].split()[0])

			assert args[8].endswith('emissions'), Flight.assert_error(8)
			emission_val = args[8].split()[0]
			self._emissions = 0 if emission_val == 'Avg' else int(emission_val[:-1])

			assert args[9].startswith('$'), Flight.assert_error(9)
			self._price = int(args[9][1:])

	@staticmethod
	def dataframe(flights):
		data = {
			'Departure datetime': [],
			'Arrival datetime': [],
			'Airline(s)' : [],
			'Travel Time' : [],
			'Origin' : [],
			'Destination' : [],
			'Num Stops' : [],
			#'Layover Time' : [],
			#'Stop Location' : [],
			'CO2 Emission (kg)' : [],
			'Emission Diff (%)' : [],
			'Price ($)' : [],
			'Access Date' : []
		}

		for flight in flights:
			data['Departure datetime'] += [flight.time_leave]
			data['Arrival datetime'] += [flight.time_arrive]
			
			data['Airline(s)'] += [flight.airline]
			data['Travel Time'] += [flight.flight_time]
			data['Origin'] += [flight.origin]
			data['Destination'] += [flight.dest]

			data['Num Stops'] += [flight.num_stops]
			#data['Layover'] += [flight.stops]
			#data['Stop Location'] += [flight.stops]
			data['CO2 Emission (kg)'] += [flight.co2]
			data['Emission Diff (%)'] += [flight.emissions]
			data['Price ($)'] += [flight.price]
			data['Access Date'] += [datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)]

		return pd.DataFrame(data)


	@staticmethod
	def assert_error(x):
		return [
			"Parsing Arg 0 as Date Leave elem is incorrect.",
			"Parsing Arg 1 as Date Return elem is incorrect.",
			-1,
			-1,
			-1,
			"Parsing Arg 6 as num stop elem is incorrect."
			"Parsing Arg 7 as CO2 elem is incorrect.",
			"Parsing Arg 8 as emissions elem is incorrect.",
			"Parsing Arg 9 as price elem is incorrect."
		][x]
