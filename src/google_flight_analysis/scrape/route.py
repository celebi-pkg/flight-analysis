'''
	How do we want to treat routes?

	Is it that we have a route IST -> JFK
	for example and keep recording for that?

	At the end of the day, we'll be storing in a DB


	While scraping: consider
	result is list of Routes: [
		Route(IST, JFK)
		Route(IST, JFK)
	]

	We can do one of two things:
	1. Create a MultiRoute object that
	holds a list of addresses to Routes
	2. Treat Route like a LinkedList
'''

class Route:

	def __init__(self, origin, destination):
		...

class OneWay(Route):

	...

class RoundTrip(Route):

	...