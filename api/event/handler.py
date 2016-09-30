import sys, os, copy, hashlib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))) # we need to add the parent directory to the path so we can share tools.py
from tools import Microservice, Credentials, Request

def generate_hash(identifier_sf_id, logged_at):
	join = str(identifier_sf_id) + str(logged_at)
	hash = hashlib.md5(join)
	return hash.hexdigest()


def event(event, context):
	r = Request(event.get('body'))
	print dict(r)
	print r.event
	functions = Microservice(context.function_name)
	body = event.get('body')
	# Decrypt Auth
	credentials = Credentials(body.get('client_id'), functions)
	
	if not hasattr(credentials, 'username'):
		return {'Error' : 'Unable to find client id'}

	# Get Triggering Object Id
	try:
		credentials.__dict__.update({
			'sf_object_id' : body['sf_object_id'], #hardcoded to get the account
			'sf_field_id' : body['sf_field_id'],
			'sf_field_value' : body['sf_field_value'],
			'sf_select_fields' : ['Id'] # only interested in the Id
		})
		record = functions.request('salesforce-rest', 'get', credentials.__dict__)
	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}

	# Handler No Triggering Object Id
	if record is None: #No triggering object found
		#What do we do here?
		return { "Error" : "No Such Triggering Object Found: %s" %  body['sf_field_value']}
	
	# Performing a 'Put' will Get The Id of the User Usage History Event Type or create a new one
	try:
		credentials.__dict__.update({
			'sf_object_id' : 'User_Usage_History_Event_Type__c', #hardcoded to get the account
			'sf_field_id' : 'Name',
			'sf_field_value' : body['event']['event_name'],
			'sf_values' : {
				'Name' : body['event']['event_name']  #TODO Fix #15 so we don't need to do this
			},
			'sf_select_fields' : ['Id'] # only interested in the Id
		})
		event = functions.request('salesforce-rest','put', credentials.__dict__)
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
			'Event_Date_Created_UNIX__c' : body['event']['event_timestamp'],
			'Saasli_Event_Id__c' : generate_hash( record['Id'], body['event']['event_timestamp']) #TODO Fix #15 so we don't need to do this
		}

		credentials.__dict__.update({
			'sf_object_id' : 'User_Usage_History__c', #hardcoded to put the User_Usage_History__c
			'sf_field_id' : 'Saasli_Event_Id__c',
			'sf_field_value' : generate_hash( record['Id'], body['event']['event_timestamp']),
			'sf_values' : sf_values
		})
	except KeyError, e:
		return {'Error' : 'Missing Parameter: %s' % e}
	
	# Upsert the event record
	return functions.request('salesforce-rest', 'put', credentials.__dict__)

def events(event, context):
	return {'Message' : 'Unimplemented'}