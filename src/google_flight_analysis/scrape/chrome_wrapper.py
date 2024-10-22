class Driver:

	def __init__(self):
		chromedriver_autoinstaller.install() # check if chromedriver is installed correctly and on path
		
		self.options = Options()
		self.options.add_argument('--no-sandbox')
		self.options.add_argument("--headless")
		self.options.add_argument('--disable-dev-shm-usage')
		
		self.driver = webdriver.Chrome(options = options)
		self.driver.maximize_window()

	'''
		query -- an xpath query
	'''
	def get(self, url, query, wait = 5):
		self.driver.get(url)

		apply_query = lambda driver, query: driver.find_element(by = By.XPATH, value = query).text.split('\n')

		WebDriverWait(self.driver, timeout = wait).until(lambda driver: len(apply_query(d, query)) > 100)

		return apply_query(self.driver, query)



	def quit(self):
		self.driver.quit()