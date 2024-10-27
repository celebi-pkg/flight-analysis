import logging
from tqdm.notebook import tqdm
# ------------------------------------------
from src.google_flight_analysis.config import config
from src.google_flight_analysis.scrape.chrome_wrapper import ChromeDriverWrapper


logger = logging.getLogger(__name__)

def scrape \
	(
		driver, origin, dest, type = 'one+way', date = None,
		instruction_config = config.instructions['specific-v1.3-a']
	):

	url = f'https://www.google.com/travel/flights?hl=en&q=Flights+to+{dest}+from+{origin}+{type}'

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

	fields = ['departure_time', 'arrival_time', 'flight_duration', 'stops', 'emissions', 'price']
	res = {field: [] for field in fields}
	for flight_item in tqdm([top_flights, other_flights]):
		for field in fields:
			res[field] += driver.instructions(
				manual = instruction_config[field],
				items = flight_item
			)

	assertions(res)

	return res

def assertions(res):
	return

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

	

