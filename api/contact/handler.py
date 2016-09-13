from tools import Microservice, Credentials
functions = Microservice() # a global instantiation of the boto lambda abstraction

def contact(event, context):
	body = event.get('body')
	try:
		# Get the Salesforce Credentials & add to query payload
		credentials = Credentials(body.get('client_id'))
		account_payload = credentials.__dict__

		# Get the Account Id
		account_payload['sf_object_id'] = 'Account' #hardcoded to get the account
		account_payload['sf_field_id'] = body.get('sf_account_field_id')
		account_payload['sf_field_value'] = body.get('sf_account_field_value')
		account_payload['sf_select_fields'] = ["Id"] # only interested in the Id
		account = functions.request('salesforce-rest-dev-get', account_payload)
	except:
		return {'Error' : 'Unable to Retrieve Account'}
	try:
		if account is not None:
			# Add the Account Id to the sf_values
			contact_payload = credentials.__dict__ #instantiate a contact upsert payload
			contact_payload['sf_object_id'] = 'Contact'
			contact_payload['sf_field_id'] = body.get('sf_field_id')
			contact_payload['sf_field_value'] = body.get('sf_field_value')
			
			contact_values = body.get('sf_values')
			contact_values['AccountId'] = account.get('Id') #include the AccountId as a sf_value
			contact_payload['sf_values'] = contact_values
			print contact_payload
		else:
			print "Nothing"
			#Do Something about no Account
	except:
		return {'Error' : 'Unable to Set Contact Values'}
	try:
		# Put the contact record
		contact_payload['sf_object_id'] = 'Contact' #hardcoded to access the contact
		contact_payload['sf_field_id'] = body.get('sf_field_id')
		contact_payload['sf_field_value'] = body.get('sf_field_value')
		response = functions.request('salesforce-rest-dev-put', contact_payload)
		return response
	except:
		return {'Error' : 'Unable to Upsert the Contact'}
	

def contacts(event, context):
	return { "message": "Go Serverless v1.0! Your function executed successfully!", "event": event }