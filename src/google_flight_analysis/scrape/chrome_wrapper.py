class ChromeDriverWrapper:

	def __init__(self, config):
		# how does htis work??
		chromedriver_autoinstaller.install() # check if chromedriver is installed correctly and on path
		
		self.config = config
		self.options = Options()
		for option in self.config['options']:
			self.options.add_argument(option)
		
		self.driver = webdriver.Chrome(options = options)
		self.driver.maximize_window()

	'''
		query -- an xpath query
	'''
	def get(self, url, query = None, wait = None):

		if query is None:
			query = self.config['query']
		if wait is None:
			wait = self.config['wait']

		self.driver.get(url)

		apply_query = lambda driver, query: driver.find_element(by = By.XPATH, value = query).text.split('\n')

		WebDriverWait(self.driver, timeout = wait).until(lambda driver: len(apply_query(d, query)) > 100)

		return apply_query(self.driver, query)



	def quit(self):
		self.driver.quit()