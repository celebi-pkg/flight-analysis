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
		self._stops = None
		self._co2 = None
		self._emissions = None
		self._price = None
		self._times = []
		self._time_leave = None
		self._time_arrive = None
		self._trash = []

		self._parse_args(*args)

	def __repr__(self):
		return "__repr__ To be Implemented"

	def __str__(self):
		return "__str__ To be Implemented"

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

	def _classify_arg(self, arg):
		if ('AM' in arg or 'PM' in arg) and len(self._times) < 2:
			# arrival or departure time
			delta = timedelta(days = 0)
			if arg[-2] == '+':
				delta = timedelta(days = int(arg[-1]))
				arg = arg[:-2]

			date_format = "%Y-%m-%d %I:%M%p"
			self._times += [datetime.strptime(self._date + " " + arg, date_format) + delta]

		elif ('hr' in arg or 'min'in arg) and self._flight_time is None:
			# flight time
			self._flight_time = arg
		elif 'stop' in arg and self._num_stops is None:
			# num stops
			self._num_stops = 0 if arg == 'Nonstop' else int(arg.split()[0])

		elif arg.endswith('CO2') and self._co2 is None:
			# co2
			self._co2 = int(arg.split()[0])
		elif arg.endswith('emissions') and self._emissions is None:
			# emmision
			emission_val = arg.split()[0]
			self._emissions = 0 if emission_val == 'Avg' else int(emission_val[:-1])
		elif '$' in arg and self._price is None:
			# price
			self._price = int(arg[1:].replace(',',''))
		elif len(arg) == 6 and arg.isupper() and self._origin is None and self._dest is None:
			# origin/dest
			self._origin = arg[:3]
			self._dest = arg[3:]
		elif ('hr' in arg and arg[-3:].isupper()) or (len(arg.split(', ')) > 1 and arg.isupper()):
			# 1 stop + time at stop
			# or multiple stops
			self._stops = arg
		elif len(arg) > 0 and arg != 'Separate tickets booked together' and arg != 'Change of airport':
			val = arg.split(',')
			val = [elem.split('Operated')[0] for elem in val]
			self._airline = ','.join(val)
		else:
			self._trash += [arg]
			# airline and other stuff idk

		if len(self._times) == 2:
			self._time_leave = self._times[0]
			self._time_arrive = self._times[1]

	def _parse_args(self, args):
		for arg in args:
			self._classify_arg(arg)

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
			'Layover' : [],
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
			data['Layover'] += [flight.stops]
			#data['Stop Location'] += [flight.stops]
			data['CO2 Emission (kg)'] += [flight.co2]
			data['Emission Diff (%)'] += [flight.emissions]
			data['Price ($)'] += [flight.price]
			data['Access Date'] += [datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)]

		return pd.DataFrame(data)


	@staticmethod
	def assert_error(x, arg):
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
		][x] + ": " + arg
