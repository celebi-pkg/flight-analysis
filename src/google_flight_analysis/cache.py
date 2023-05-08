'''/****************************************************************************************************************************************************************
  Written by Kaya Celebi, April 2023
****************************************************************************************************************************************************************/'''

import numpy as np
import pandas as pd
from tqdm import tqdm
from datetime import date, datetime, timedelta
import sqlite3
import json
import os

__all__ = ['CacheControl']

class _CacheControl:

	def __init__(self):
		self.directory = None
		self.access = None
	'''
		args = root, obj(Scrape), obj(Scrape) ..., db?
	'''
	def __call__(self, *args):
		self.directory, self.access = _CacheControl._check_dir(args[0])
		for obj in tqdm(args[1:-1], desc = "Caching Data"):
			if _CacheControl._check_scrape(obj):
				self.cache(obj, args[-1])

	def __str__(self):
		return "Function to store scraped data."

	def __repr__(self):
		return "<Function to store scraped data: CacheControl>"

	def cache(self, obj, db):
		fname = self.directory + _CacheControl._get_file_name(obj.origin, obj.dest, access = False)
		access = self.access + _CacheControl._get_file_name(obj.origin, obj.dest, access = True)
		df = obj.data
		current_access = df['Access Date'].values[0]

		if db:
			...

		# If file already exists
		if os.path.isfile(fname):
			# Check if most recent access is today
			with open(access) as file:
				recent_access = file.readline()
				if recent_access != current_access:
					df_old = pd.read_csv(fname, index_col = 'Unnamed: 0')
					df = pd.concat([df_old, df], ignore_index = True)
				else:
					return # Data already in csv, redundant

		df.to_csv(fname)
		with open(access, 'w') as file:
			file.write(current_access)


	def connect_db(self):
		conn = sqlite3.connect(self.directory + 'flights.db')

		return conn

	def disconnect_db(self, conn):
		conn.close()

	def create_table():
		...


	'''
		Check that the scraping instance is valid
	'''
	@staticmethod
	def _check_scrape(arg):
		return True#isinstance(arg, _Scrape)

	'''
		Check root directory formatting
	'''
	@staticmethod
	def _check_dir(arg):
		arg = arg if arg[-1] == '/' else arg + '/'

		# Initializing .access metadata for new directory type
		if not os.path.exists(arg + '.access/'):
			os.system('mkdir {dir}.access'.format(dir = arg))

		return arg, arg + '.access/'
		

	'''
		Generate a filename given the object
	'''
	@staticmethod
	def _get_file_name(airport1, airport2, access):
		# create filename by alphabetical of 2 airports, regardless of origin or dest
		airports = sorted([airport1, airport2])
		file = "{}-{}".format(*airports)
		if access:
			return file + '.txt'
		return file + '.csv'



CacheControl = _CacheControl()