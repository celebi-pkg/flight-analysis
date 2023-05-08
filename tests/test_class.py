import pytest
import pandas as pd
from pathlib import Path
import os

from src.google_flight_analysis.scrape import *
from src.google_flight_analysis.cache import *

'''
	Create resilience test: run the code 3 times and check DBs the same
'''

def func_0():
	return True

res1 = pd.read_csv('tests/test_data/test1.csv')
res1 = Scrape("LGA", "RDU", "2023-05-15", "2023-06-15", res1)

res2 = pd.read_csv('tests/test_data/test2.csv')
res2 = Scrape("IST", "CDG", "2023-07-15", "2023-07-20", res2)

os.system('rm tests/test_data/LGA-RDU.csv')
os.system('rm tests/test_data/CDG-IST.csv')
os.system('rm -rf tests/test_data/.access')

CacheControl('tests/test_data/', res1, False)
CacheControl('tests/test_data/', res2, False)

def test_0():
	assert func_0(), "Test 0 Failed"

#-------QUERY 1

def test_1():
	assert res1.data.shape[0] > 0, "Test 1 Failed."

def test_2():
	assert res1.origin == "LGA", "Test 2 Failed."

def test_3():
	assert res1.dest == "RDU", "Test 3 Failed."

def test_4():
	assert res1.date_leave == "2023-05-15", "Test 4 Failed."

def test_5():
	assert res1.date_return == "2023-06-15", "Test 5 Failed."

#-------QUERY 2

def test_6():
	assert res2.data.shape[0] > 0, "Test 6 Failed."

def test_7():
	assert res2.origin == "IST", "Test 7 Failed."

def test_8():
	assert res2.dest == "CDG", "Test 8 Failed."

def test_9():
	assert res2.date_leave == "2023-07-15", "Test 9 Failed."

def test_10():
	assert res2.date_return == "2023-07-20", "Test 10 Failed."

#-------CACHE 1

def test_11():
	assert os.path.isfile('tests/test_data/LGA-RDU.csv'), "Test 11 Failed."

def test_12():
	df = pd.read_csv('tests/test_data/LGA-RDU.csv')
	assert df.shape[0] > 0 and df.shape[1] > 0, "Test 12 Failed."

def test_13():
	assert os.path.isfile('tests/test_data/CDG-IST.csv'), "Test 13 Failed."

def test_14():
	df = pd.read_csv('tests/test_data/CDG-IST.csv')
	assert df.shape[0] > 0 and df.shape[1] > 0, "Test 14 Failed."
