from selenium.webdriver.common.by import By

chrome_driver = \
		{
			'v1': {
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
				'wait' : 5,
				'by': By.XPATH
			},
			'debug': {
				'options': [
					'--no-sandbox'
				],
				'query': '//li',
				'query_lim': 0,
				'wait' : 5,
				'by': By.XPATH
			}
		}

instructions = \
		{
			'v1': { #//find elements
				'flight_items': [
					('find_element', "//c-wiz[@jsrenderer = 'p4IKPb']"),
					('find_element', "//div[@jsname = 'KL7Kx']"),
					('find_element', "//div[@class = 'VfPpkd-dgl2Hf-ppHlrf-sM5MNb']"),
					('find_element', "//button[@class = 'VfPpkd-LgbsSe VfPpkd-LgbsSe-OWXEXe-k8QpJ VfPpkd-LgbsSe-OWXEXe-Bz112c-M1Soyc VfPpkd-LgbsSe-OWXEXe-dgl2Hf nCP5yc AjY5Oe LQeN7 nJawce OTelKf iIo4pd']"),
					('-- assertion'),
					('click'),
					('wait 5 seconds'),
					('get_until'),
					# assertion
					('find_elements', "//li[@class = 'pIav2d']")
				],
				'arrival_departure': [
					('find_elements', "//span[@jscontroller = 'cNtv4b']")
				],
				'price': [
					...
				],
				'price': [
					...
				],
				'emissions': [
					...
				],


			}
		}

cache = \
		{
			'v1': {
				0:1
			}
		}