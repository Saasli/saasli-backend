from tools import Microservice, Credentials
functions = Microservice() # a global instantiation of the boto lambda abstraction

def account(event, context):
	try:
		# Get the Salesforce Credentials & add to query payload
		credentials = Credentials(event.get('body').get('id'))
		query_payload = credentials.__dict__
		# Get the first record
		query_payload['sf_object_id'] = 'Contact'
		query_payload['sf_field_id'] = 'Email'
		query_payload['sf_field_value'] = 'hgoddard@saasli.com'
		query_payload['sf_select_fields'] = ['Id', 'Name']
		response = functions.request('salesforce-rest-dev-get', query_payload)
		print response
	except:
		response = {'Error' : 'Invalid Parameters'}
	return response