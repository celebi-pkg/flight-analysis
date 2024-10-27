import logging
from tqdm.notebook import tqdm
import pandas as pd
# ------------------------------------------
from src.google_flight_analysis.config import config


logger = logging.getLogger(__name__)

def scrape \
	(
		driver, url,
		instruction_config = config.instructions['specific-v1.3-a']
	):

	logger.info('Getting URL with driver')
	driver.get(url)

	# make entry query
	out = driver.instructions(
		manual = instruction_config['entry_query'],
		items = driver
	)

	# get flights from Google top flight section
	top_flights = driver.instructions(
		manual = instruction_config['top_flight_items'],
		items = out
	)

	# get flights from other flights section after button click
	other_flights = driver.instructions(
		manual = instruction_config['other_flight_items'],
		items = out
	)

	# instruction_config.keys()[3:]
	fields = ['departure_time', 'arrival_time', 'flight_duration', 'stops', 'emissions', 'price']
	res = {field: [] for field in fields}
	for flight_item in [top_flights, other_flights]:
		for field in fields:
			res[field] += driver.instructions(
				manual = instruction_config[field],
				items = flight_item
			)

	print(assertions(res))

	return res

def format_df(res):
	df = pd.DataFrame(res)

	df.departure_date = df.departure_date.apply(lambda x: pd.to_datetime(x, format = '%Y-%m-%d'))
	df['arrival_date_offset'] = df.arrival_time.apply(lambda x: None if type(x) is WebElementWrapper else pd.Timedelta(days = int(x.split('+')[1])) if '+' in x else pd.Timedelta(days=0))
	df['arrival_date'] = df.departure_date + df.arrival_date_offset

	df.departure_time = df.departure_time.apply(lambda x: pd.Timedelta(pd.Timestamp(x).hour*60 + pd.Timestamp(x).minute, unit = 'min'))
	df.arrival_time = df.arrival_time.apply(lambda x: None if type(x) is WebElementWrapper else  x.split('+')[0] if '+' in x else x)
	df.arrival_time = df.arrival_time.apply(lambda x: pd.Timedelta(pd.Timestamp(x).hour*60 + pd.Timestamp(x).minute, unit = 'min'))


	df.stops = df.stops.apply(lambda x: int(x.split(' ')[0]) if x != 'Nonstop' else 0)
	df.emissions = df.emissions.apply(lambda x: int(x.split(' ')[0].replace(',','')))
	df.price = df.price.apply(lambda x: int(x[1:].replace(',','')) if x != 'Price unavailable' else None)
	df.flight_duration = df.flight_duration.apply(lambda x: pd.Timedelta(x))

	df['date_collected'] = pd.to_datetime('today')

	return df[['origin', 'dest', 'date_collected', 'departure_date', 'departure_time', 'arrival_date', 'arrival_time', 'arrival_date_offset', 'flight_duration', 'stops', 'emissions', 'price']]
	
def check_inputs(args):
	...

def assertions(res):
	return check_output_lengths(res)

'''
	Check that the fields all have the same length
'''
def check_output_lengths(res):
	prev = None
	for key in res:
		if prev is not None and prev != len(res[key]):
			return False
		prev  = len(res[key])

	return True

	

