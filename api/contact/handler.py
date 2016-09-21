from tools import Microservice, Credentials
functions = Microservice() # a global instantiation of the boto lambda abstraction

def contact(event, context):
	body = event.get('body')
	
	# Decrypt Auth
	credentials = Credentials(body.get('client_id'))
	
	if not hasattr(credentials, 'username'):
		return {'Error' : 'Unable to find client id'}

	# Get the Account Id
	try:
		credentials.__dict__.update({
			'sf_object_id' : 'Account', #hardcoded to get the account
			'sf_field_id' : body['sf_account_field_id'],
			'sf_field_value' : body['sf_account_field_value'],
			'sf_select_fields' : ['Id'] # only interested in the Id
		})
		account = functions.request('salesforce-rest-dev-get', credentials.__dict__)
	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}
	# Build the contact upsertion payload	
	try:
		if account.get('Id') is not None:
			body['sf_values'].update({'AccountId' : account['Id']})
		#else:
			# Do Something about no Account
			# a) 'Put' it in SF
			# b) Inform the user of failure
			# c) create conditionally on a checkbox exposed in API
		credentials.__dict__.update({
			'sf_object_id' : 'Contact',
			'sf_field_id' : body['sf_field_id'],
			'sf_field_value' : body['sf_field_value'],
			'sf_values' : body['sf_values'],
			'sf_account_id' : account['Id']
		})


	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}
	
	# Upsert the contact record
	return functions.request('salesforce-rest-dev-put', credentials.__dict__)

def contacts(event, context):
	return { "message": "Go Serverless v1.0! Your function executed successfully!", "event": event }