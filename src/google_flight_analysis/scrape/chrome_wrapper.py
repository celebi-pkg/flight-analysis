import time
from tqdm.notebook import tqdm
# ------------------------------------------
import chromedriver_autoinstaller
# ------------------------------------------
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class ChromeDriverWrapper:

	def __init__(self, config):
		chromedriver_autoinstaller.install() # check if chromedriver is installed correctly and on path
		
		self.config = config
		self.options = Options()
		for option in self.config['options']:
			self.options.add_argument(option)
		
		self.driver = webdriver.Chrome(options = self.options)
		self.driver.maximize_window()

	'''
		query -- an xpath query
	'''
	def get(self, url):
		self.driver.get(url)

	# the instruction manual is some config
	def instructions(self, manual, items):
		for idx, batch in enumerate(manual['batches']):
			curr = items
			for instruction, *args in tqdm(batch, desc = f'Batch #{idx}'):
				if type(curr) == list: # result of a previous find_elements
					curr = [getattr(elem, instruction)(*args) for elem in curr]
				else:
					curr = getattr(curr, instruction)(*args)

		return curr

	def get_until(query = None, wait = None, query_lim = None):
		if query is None:
			query = self.config['query']
		if wait is None:
			wait = self.config['wait']
		if query_lim is None:
			query_lim = self.config['query_lim']

		#...
		return

	def assertion(self):
		#...
		return

	def wait(self, wait = None):
		if wait is None:
			wait = self.config['wait']
		time.sleep(wait)
		return self

	def click(self, *args):
		self.driver.click()
		return self

	def get_attribute(self, attr):
		return self.driver.get_attribute(attr)

	# this always outputs WebElementWrapper
	def find_element(self, query):
		return WebElementWrapper(
			web_element = self.driver.find_element(self.config['by'], query),
			config = self.config
		)

	# this always outputs List[WebElementWrapper]
	def find_elements(self, query):
		return [
			WebElementWrapper(web_element = x, config = self.config)
			for x in self.driver.find_elements(self.config['by'], query)
		]

	def quit(self):
		self.driver.quit()

class WebElementWrapper(ChromeDriverWrapper):

	def __init__(self, web_element, config):
		self.config = config
		self.web_element = web_element

	def click(self, *args):
		self.web_element.click()
		return self

	def text(self, *args):
		return self.web_element.text

	def get_attribute(self, attr):
		return self.web_element.get_attribute(attr)

	# this always outputs WebElementWrapper
	def find_element(self, query):
		return WebElementWrapper(
			web_element = self.web_element.find_element(self.config['by'], query),
			config = self.config
		)

	# this always outputs List[WebElementWrapper]
	def find_elements(self, query):
		return [
			WebElementWrapper(web_element = x, config = self.config)
			for x in self.web_element.find_elements(self.config['by'], query)
		]

	# condition = lambda result, args: result == args...
	def assertion(self, func, condition_func, *func_args, **condition_func_args):
		assert condition_func(getattr(self.web_element, func)(*args), **condition_func_args)

		return self


