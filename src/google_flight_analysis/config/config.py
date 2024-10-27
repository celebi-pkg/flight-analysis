from selenium.webdriver.common.by import By

chrome_driver = \
		{
			'v0-a': {
				'options': [
					'--no-sandbox',
					'--headless',
					'--disable-dev-shm-usage'
				],
				'query': '//body[@id = "yDmH0d"]',
				'query_lim': 100,
				'wait' : 10,
				'by': By.XPATH
			},
			'dummy': {
				'options': [
					'--no-sandbox',
					'--headless',
					'--disable-dev-shm-usage'
				],
				'query': '//div',
				'query_lim': 0,
				'wait' : 3,
				'by': By.XPATH
			},
			'debug': {
				'options': [
					'--no-sandbox',
					'--disable-dev-shm-usage'
				],
				'query': '//li',
				'query_lim': 0,
				'wait' : 5,
				'by': By.XPATH
			}
		}

# the future ---- how to automate this research?
# these queries need to be streamlined, we can probably get it all in one big line

# each instruction within a batch is a (function, query) pair
# every batch always starts as a ChromeDriver object then can become a web object

# Let's make sure to take care with:
# NoSuchElementException
instructions = \
		{
			'shortcut-query-v1.3-a': \
			{
				'flight_items': {
					'batches': [
						[
							('find_element', "//c-wiz[@jsrenderer = 'p4IKPb']"),
							('find_element', "//div[@jsname = 'KL7Kx']"),
							('find_element', "//div[@class = 'VfPpkd-dgl2Hf-ppHlrf-sM5MNb']"),
							('find_element', "//button[@class = 'VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-Bz112c-M1Soyc VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe LQeN7 nJawce OTelKf iIo4pd']"),
							#('-- assertion'),
							('click', None)
							#('get_until')
							# assertion
							
						],
						[
							('wait', None), # driver
							('find_elements', "//li[@class = 'pIav2d']")
						]
					],
					'description': '''Batch processes to query for each flight item. We want a list of each 
					flight item as it shows on Google flights. We first need to find the button title xx more flights
					and click it. Then, scrape for the elements'''
				},
				'departure_arrival': {
					'batches': [
						[
							('find_elements', "//span[@jscontroller = 'cNtv4b']"),
							('get_attribute', 'aria-label')
						]
					],
					'description': '''Obtaining departure and arrival times'''
				}
			},
			'specific-v1.3-a': \
			{
				'entry_query' : \
				{
					'batches': \
					[
						[
							('wait', 2),
							('find_element', '//*[@id="yDmH0d"]/c-wiz[2]/div/div[2]/c-wiz/div[1]/c-wiz/div[2]/div[2]/div[2]/div/div[2]') # first_subquery
						]
					],
					'description' : 'Opening query to focus future queries on relevant subdomain'
				},
				'top_flight_items':
				{
					'batches': \
					[
						[
							('find_element', './div[1]') # gives <ul> with all top flights
						]
					],
					'description' : 'Get the <ul> for top/best flight items'
				},
				'other_flight_items' : \
				{
					'batches': \
					[
						[
							('find_element', './div[4]/ul//li/div/span[1]/div/button'), # find button
							('click', None) # click button
						],
						[
							('wait', None), # driver wait
							('find_element', './div[4]') # get flight <ul> with all other flights
						]
					],
					'description' : 'Click other flights button and get <ul> with all other flights'
				},
				'departure_time': \
				{
					'batches': \
					[
						[
							('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/span/span[1]/span/span/span'),
							('text', None)
						]
					],
					'description' : 'Get departure times'
				},
				'arrival_time': \
				{
					'batches': \
					[
						[
							('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/span/span[2]/span/span/span'),
							('text', None)
						]
					],
					'description' : 'Get arrival times'
				},
				'flight_duration': \
				{
					'batches': \
					[
						[
							('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[3]/div'),
							('text', None)
						]
					],
					'description' : 'Get the flight duration'
				},
				'stops': \
				{
					'batches': \
					[
						[
							('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[4]/div[1]/span'),
							('text', None)
						]
					],
					'description' : 'Get the number of stops for this route'
				}, # handles stop time, etc
				'emissions': \
				{
					'batches': \
					[
						[
							('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[5]/div/div[1]/div'),
							('text', None)
						]
					],
					'description' : 'Get departure times'
				},
				'emissions_avg_dif': \
				{
					'batches': \
					[
						[
							('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[5]/div/div[2]/div[1]'),
							('text', None)
						]
					],
					'description' : 'Get departure times'
				},
				'price': \
				{
					'batches': \
					[
						[
							('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[6]/div[1]/div[2]/span'),
							#('find_elements', './ul//li/div/div[2]/div/div[2]/div[1]/div[6]/div[1]/div/span'),
							('text', None)
						]
					],
					'description' : 'Get departure times'
				}
			}
		}

cache = \
		{
			'v1': {
				0:1
			}
		}