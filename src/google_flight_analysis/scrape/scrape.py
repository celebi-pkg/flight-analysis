from src.google_flight_analysis.config import config
from src.google_flight_analysis.chrome_wrapper import ChromeDriverWrapper



def scrape(origin, dest):
	driver = ChromeDriverWrapper(config = config.chrome_driver['dummy'])
	url = f'https://www.google.com/travel/flights?hl=en&q=Flights+to+{dest}+from+{origin}+one+way'

	driver.get(url)

	# make entry query
	out = driver.instructions(
		manual = config.instructions['specific-v1.3-a']['entry_query'],
		items = driver
	)

	# get flights from Google top flight section
	top_flights = driver.instructions(
		manual = config.instructions['specific-v1.3-a']['top_flight_items'],
		items = driver
	)

	other_flights = driver.instructions(
		manual = config.instructions['specific-v1.3-a']['other_flight_items'],
		items = driver
	)

	# get departure + arrival times
	manual = config.instructions['v0-a']['departure_arrival']
	times = driver.instructions(manual)
	times = [x for x in times if x[:9] == 'Departure' or x[:7] == 'Arrival']

	

