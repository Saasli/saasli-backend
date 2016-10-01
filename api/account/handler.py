import sys, os, copy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))) # we need to add the parent directory to the path so we can share tools.py
from tools import Microservice, Credentials, Request

#Expecting a payload as defined here: https://saasli.github.io/docs/#account
def account(event, context):
	request = Request(event.get('body'), event.get('path'))
	print dict(request)
	functions = Microservice(context.function_name.split('-')[1])
	body = event.get('body')

	try:
		# Get the Salesforce Credentials & add to query payload
		credentials = Credentials(body.get('client_id'), functions)

		if not hasattr(credentials, 'username'):
			return {'Error' : 'Unable to find client id'}

		credentials.__dict__.update({
			'sf_object_id' : 'Account', #hardcoded by virtue of endpoint being Account
			'sf_field_id' : request.account_field,
			'sf_field_value' : request.account_value,
			'sf_values' : request.account
		})
		# Get the first record
		response = functions.request('salesforce-rest', 'put', credentials.__dict__)
	except KeyError, e:
		response = {'Error' : 'Invalid Parameters %s' % e}
	return response

def accounts(event, context):
	return {'Message' : 'Unimplemented'}