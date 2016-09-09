from tools import Microservice, Credentials
import json
functions = Microservice() # a global instantiation of the boto lambda abstraction

def account(event, context):
	try:
		# Get the Salesforce Credentials
		credentials = Credentials(event.get('body').get('id'))
		response = credentials.__dict__
	except:
		response = {'Error' : 'Invalid Parameters'}
	return response