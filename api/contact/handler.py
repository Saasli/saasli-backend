import sys, os, copy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))) # we need to add the parent directory to the path so we can share tools.py
from tools import Microservice, Credentials, Request

def contact(event, context):
	functions = Microservice(context.function_name)
	request = Request(event.get('body'), event.get('path'))
	# Decrypt Auth
	credentials = Credentials(request.client_id, functions)
	
	if not hasattr(credentials, 'username'):
		return {'Error' : 'Unable to find client id'}

	# Get the Account Id
	try:
		credentials.__dict__.update({
			'sf_object_id' : 'Account', #hardcoded to get the account
			'sf_field_id' : request.account_field,
			'sf_field_value' : request.account_value,
			'sf_select_fields' : ['Id'] # only interested in the Id
		})
		account = functions.request('salesforce-rest', 'get', credentials.__dict__)
		print account
	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}
	# Build the contact upsertion payload	
	try:
		#else:
			# Do Something about no Account
			# a) 'Put' it in SF
			# b) Inform the user of failure
			# c) create conditionally on a checkbox exposed in API
		credentials.__dict__.update({
			'sf_object_id' : 'Contact',
			'sf_field_id' : request.contact_field,
			'sf_field_value' : request.contact_value,
			'sf_values' : request.contact,
			'sf_account_id' : account['Id']
		})


	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}
	
	# Upsert the contact record
	return functions.request('salesforce-rest', 'put', credentials.__dict__)

def contacts(event, context):
	return { "message": "Go Serverless v1.0! Your function executed successfully!", "event": event }