from tools import Microservice
functions = Microservice() # a global instantiation of the boto lambda abstraction

def account(event, context):
	payload = {'parameter' : 'value'}

	response = functions.request('salesforce-dev-get', payload)
	message = response.get('message')
	back = response.get('back')
	return { "message from lib": message, "paramter passed through" : back }