from tools import Microservice, Credentials
functions = Microservice() # a global instantiation of the boto lambda abstraction


#Expecting a payload as defined here: https://saasli.github.io/docs/#account
def account(event, context):
	body = event.get('body')
	try:
		# Get the Salesforce Credentials & add to query payload
		credentials = Credentials(body.get('client_id'))
		account_payload = credentials.__dict__
		# Get the first record
		account_payload['sf_object_id'] = 'Account' #hardcoded by virtue of endpoint being Account
		account_payload['sf_field_id'] = body.get('sf_field_id')
		account_payload['sf_field_value'] = body.get('sf_field_value')
		account_payload['sf_values'] = body.get('sf_values')
		response = functions.request('salesforce-rest-dev-put', account_payload)
		print response
	except:
		response = {'Error' : 'Invalid Parameters'}
	return response

def accounts(event, context):
	return {'Message' : 'Unimplemented'}