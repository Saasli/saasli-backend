import hashlib
from tools import Microservice, Credentials
functions = Microservice() # a global instantiation of the boto lambda abstraction

def generate_hash(identifier_sf_id, logged_at):
	join = str(identifier_sf_id) + str(logged_at)
	hash = hashlib.md5(join)
	return hash.hexdigest()

def event(event, context):
	body = event.get('body')
	# Decrypt Auth
	try:
		# Get the Salesforce Credentials
		credentials = Credentials(body.get('client_id'))
	except Exception, e:
		return {'Error' : 'Unable to Retrieve Authenticate With Salesforce. Have your credentials change? If so please notify Saasli'}

	# Get Triggering Object Id
	try:
		credentials.__dict__.update({
			'sf_object_id' : body['sf_object_id'], #hardcoded to get the account
			'sf_field_id' : body['sf_field_id'],
			'sf_field_value' : body['sf_field_value'],
			'sf_select_fields' : ['Id'] # only interested in the Id
		})
		record = functions.request('salesforce-rest-dev-get', credentials.__dict__)
	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}

	# Handler No Triggering Object Id
	if record.get('Id') is None: #No triggering object found
		#What do we do here?
		return { "Error" : "No Such Triggering Object Found: %s" %  body['sf_field_value']}
	
	# Performing a 'Put' will Get The Id of the User Usage History Event Type or create a new one
	try:
		credentials.__dict__.update({
			'sf_object_id' : 'User_Usage_History_Event_Type__c', #hardcoded to get the account
			'sf_field_id' : 'Name',
			'sf_field_value' : body['event']['name'],
			'sf_values' : {
				'Name' : body['event']['name']  #TODO Fix #15 so we don't need to do this
			},
			'sf_select_fields' : ['Id'] # only interested in the Id
		})
		event = functions.request('salesforce-rest-dev-put', credentials.__dict__)
	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}


	# Build the User Usage History upsert
	try:
		print event
		print event.get('Id')
		#build the event sf_values
		sf_values = {
			body['sf_object_id'] + '__c' : record.get('Id'), #polymorphic relating id
			'User_Usage_History_Event_Type__c' : event['Id'],
			'Event_Date_Created_UNIX__c' : body['event']['logged_at'],
			'Saasli_Event_Id__c' : generate_hash( record['Id'], body['event']['logged_at']) #TODO Fix #15 so we don't need to do this
		}

		credentials.__dict__.update({
			'sf_object_id' : 'User_Usage_History__c', #hardcoded to put the User_Usage_History__c
			'sf_field_id' : 'Saasli_Event_Id__c',
			'sf_field_value' : generate_hash( record['Id'], body['event']['logged_at']),
			'sf_values' : sf_values
		})
	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}
	
	# Upsert the event record
	return functions.request('salesforce-rest-dev-put', credentials.__dict__)

def events(event, context):
	return {'Message' : 'Unimplemented'}