import pytest
import pandas as pd
from pathlib import Path
import os

from google_flight_analysis.scrape import *
from google_flight_analysis.cache import *

'''
	Create resilience test: run the code 3 times and check DBs the same
'''

def func_0():
	return True

# Filled queries
res1 = Scrape("LGA", "RDU", "2023-05-15", "2023-06-15")
res1.data = pd.read_csv('tests/test_data/test1.csv')

res2 = Scrape("IST", "CDG", "2023-07-15", "2023-07-20",)
res2.data = pd.read_csv('tests/test_data/test2.csv')

# Empty queries

# One way
res3 = Scrape("FCO", "IST", "2023-12-05")
res4 = Scrape("CDG", "JFK", "2023-12-15")

#chain trip
res5 = Scrape("JFK", "AMS", "2023-11-10", "CDG", "AMS", "2023-11-17", "AMS", "IST", "2023-11-25")

# perfect chain
res6 = Scrape("JFK", "2023-11-10", "AMS", "2023-11-17", "CDG", "2023-11-20", "IST", "2023-11-25", "JFK")

# addition tests
res7 = Scrape("JFK", "IST", "2023-12-05")
res8 = Scrape("IST", "JFK", "2023-12-30")

res9 = Scrape("JFK", "IST", "2023-12-05", "2023-12-30")
res10 = Scrape("JFK", "CDG", "2024-01-10", "2024-02-10")


print(res9.origin[0] == res10.origin[0], res9.type, res10.type)

print('12')
out12 = res1 + res2
print('78')
out78 = res7 + res8
print('910')
out910 = res9 + res10
print('done?')

'''os.system('rm tests/test_data/LGA-RDU.csv')
os.system('rm tests/test_data/CDG-IST.csv')
os.system('rm -rf tests/test_data/.access')

CacheControl('tests/test_data/', res1, False)
CacheControl('tests/test_data/', res2, False)'''

def test_0():
	assert func_0(), "Test 0 Failed"

#-------QUERY 1

def test_1():
	assert res1.data.shape[0] > 0, "Test 1 Failed."

def test_2():
	assert res1.origin[0] == "LGA", "Test 2 Failed."

def test_3():
	assert res1.dest[0] == "RDU", "Test 3 Failed."

def test_4():
	assert res1.date[0] == "2023-05-15", "Test 4 Failed."

def test_5():
	assert res1.date[1] == "2023-06-15", "Test 5 Failed."

#-------QUERY 2

def test_6():
	assert res2.data.shape[0] > 0, "Test 6 Failed."

def test_7():
	assert res2.origin[0] == "IST", "Test 7 Failed."

def test_8():
	assert res2.dest[0] == "CDG", "Test 8 Failed."

def test_9():
	assert res2.date[0] == "2023-07-15", "Test 9 Failed."

def test_10():
	assert res2.date[1] == "2023-07-20", "Test 10 Failed."

#-------QUERY 3

def test_11():
	assert res3.origin[0] == "FCO", "Test 11 Failed."

def test_12():
	assert res3.dest[0] == "IST", "Test 12 Failed."

def test_13():
	assert res3.date[0] == "2023-12-05", "Test 13 Failed."

#-------QUERY 4

def test_14():
	assert res4.origin[0] == "CDG", "Test 14 Failed."

def test_15():
	assert res4.dest[0] == "JFK", "Test 15 Failed."

def test_16():
	assert res4.date[0] == "2023-12-15", "Test 16 Failed."

#-------QUERY 5

def test_17():
	assert res5.origin == ["JFK", "CDG", "AMS"], "Test 17 Failed."

def test_18():
	assert res5.dest == ["AMS", "AMS", "IST"], "Test 18 Failed."

def test_19():
	assert res5.date == ["2023-11-10", "2023-11-17", "2023-11-25"], "Test 19 Failed."

#-------QUERY 6

def test_20():
	assert res6.origin == ["JFK", "AMS", "CDG", "IST"], "Test 20 Failed."

def test_21():
	assert res6.dest == ["AMS", "CDG", "IST", "JFK"], "Test 21 Failed."

def test_22():
	assert res6.date == ["2023-11-10", "2023-11-17", "2023-11-20", "2023-11-25"], "Test 22 Failed."


#-------ADDITION

def test_23():
	assert out12.type == 'chain-trip', "Test 23 Failed."

def test_24():
	assert out12.data.shape[0] > 0, "Test 24 Failed."

def test_25():
	assert out78.type == 'round-trip', "Test 25 Failed."

def test_26():
	assert out910.type == 'perfect-chain', "Test 26 Failed."



'''#-------CACHE 1

def test_11():
	assert os.path.isfile('tests/test_data/LGA-RDU.csv'), "Test 11 Failed."

def test_12():
	df = pd.read_csv('tests/test_data/LGA-RDU.csv')
	assert df.shape[0] > 0 and df.shape[1] > 0, "Test 12 Failed."

def test_13():
	assert os.path.isfile('tests/test_data/CDG-IST.csv'), "Test 13 Failed."

def test_14():
	df = pd.read_csv('tests/test_data/CDG-IST.csv')
	assert df.shape[0] > 0 and df.shape[1] > 0, "Test 14 Failed."'''
