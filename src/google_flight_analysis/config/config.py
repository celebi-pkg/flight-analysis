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
				'wait' : 10
			},
			'dummy': {
				'options': [
					'--no-sandbox',
					'--headless',
					'--disable-dev-shm-usage'
				],
				'query': '//div',
				'query_lim': 0,
				'wait' : 5
			}
		}

cache = \
		{
			'v1': {
				0:1
			}
		}