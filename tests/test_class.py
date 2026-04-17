import pytest
import pandas as pd
from pathlib import Path
import os

#from src.google_flight_analysis.scrape import *
#from src.google_flight_analysis.cache import *

from src.google_flight_analysis.config import config
from src.google_flight_analysis.scrape.chrome_wrapper import ChromeDriverWrapper

'''
	Create resilience test: run the code 3 times and check DBs the same
'''



'''
	Check that chromedriver config has all the required options --
	It can have more than just what is in the list below
'''
def func_config_chrome_driver_format():
	for x in config.chrome_driver.keys():
		for opt in ['options', 'query', 'query_lim', 'wait', 'by']:
			if opt not in config.chrome_driver[x].keys():
				return False
	return True

def func_get_example_com():


def test_tautology():
	assert 1 == 1, "Test 0 Failed"

def test_config_chrome_driver_format():
	assert func_config_chrome_driver_format(), "config not in correct format"

