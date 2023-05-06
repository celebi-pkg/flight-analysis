from datetime import date, datetime, timedelta
import numpy as np
import pandas as pd
from tqdm import tqdm

__all__ = ['Flight']


class Flight:

	def __init__(self, dl, dr, *args):
		self._id = 1
		self._origin = None
		self._dest = None
		self._date_leave = dl
		self._date_return = dr
		self._airline = None
		self._num_stops = None
		self._stops = []
		self._co2 = None
		self._emissions = None
		self._price = None
		self._trip_type = None #round trip
		self._time_leave = None
		self._time_return = None

		self._parse_args(args)


	def _parse_args(self, *args):
		self._time_leave = args[0]
		self._time_return = args[2]

		self._airline = args[4]
		self._origin = args[5][:3]
		self._dest = args[5][3:]

		self._num_stops = 0 if args[6] == 'Nonstop' else int(args[6].split('')[0])

		if self._num_stops > 0:
			self._stops += args[7:7+self._num_stops]
		else:
			assert args[7].endswith('CO2'), 'Parsing Arg 7 as CO2 elem is incorrect.'
			self._co2 = args[7].split()

	'''
		Set properties upon scraper called.
	'''
	def _set_properties(self, *args):
		(
			self._origin, self._dest, self._date_leave, self._date_return
		) = args

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
