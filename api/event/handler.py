import hashlib
from event.brokers import EventRequest
from tools import *

def generate_hash(identifier_sf_id, logged_at):
	join = str(identifier_sf_id) + str(logged_at)
	hash = hashlib.md5(join)
	return hash.hexdigest()


def event(event, context):
	request = EventRequest(event, context)

	if request.triggeringrecord.sfid is not None: # Do we have a record to associate this too?
		uuh_saasli_id = generate_hash(request.triggeringrecord.sfid, request.eventtime)
		uuh_conditions = [{ 'a' : 'Saasli_Event_Id__c', 'op' : '=', 'b' : uuh_saasli_id }]
		uuh = request.salesforce_record(uuh_conditions, 'User_Usage_History__c')
		if uuh.sfid is None: # Does this event not already exist?
			uuh_values = {
				'%s__c' % request.triggeringrecordobjecttype : request.triggeringrecord.sfid, #polymorphic relating id
				'User_Usage_History_Event_Type__c' : request.userusagetype.sfid,
				'Event_Date_Created_UNIX__c' : request.eventtime
			}
			return uuh.create(uuh_values) # make the new event
		else:
			return {'Error' : 'Event Already Exists'}
	else:
		return {'Error' : 'No record to associate event to'}


def events(event, context):
	return {'Message' : 'Unimplemented'}