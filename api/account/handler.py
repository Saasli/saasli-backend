from tools import Microservice, Credentials
functions = Microservice() # a global instantiation of the boto lambda abstraction


#Expecting a payload as defined here: https://saasli.github.io/docs/#account
def account(event, context):
	body = event.get('body')
	try:
		# Get the Salesforce Credentials & add to query payload
		credentials = Credentials(body.get('client_id'))
		credentials.__dict__.update({
			'sf_object_id' : 'Account', #hardcoded by virtue of endpoint being Account
			'sf_field_id' : body['sf_field_id'],
			'sf_field_value' : body['sf_field_value'],
			'sf_values' : body['account']
		})
		# Get the first record
		response = functions.request('salesforce-rest-dev-put', credentials.__dict__)
	except KeyError, e:
		response = {'Error' : 'Invalid Parameters %s' % e}
	return response

def accounts(event, context):
	return {'Message' : 'Unimplemented'}