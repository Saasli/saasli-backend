import hashlib
from event.brokers import EventRequest
from tools import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_hash(identifier_sf_id, logged_at):
	logger.info('Generating Saasli event Id hash.')
	join = str(identifier_sf_id) + str(logged_at)
	hash = hashlib.md5(join)
	return hash.hexdigest()


def event(event, context):
	logger.info('event endpoint hit: {}'.format(event))
	request = EventRequest(event, context)

	if request.triggeringrecord.sfid is not None: # Do we have a record to associate this too?
		logger.info('Creating new event.')
		uuh_saasli_id = generate_hash(request.triggeringrecord.sfid, request.eventtime)
		uuh_conditions = [{ 'a' : 'Saasli_Event_Id__c', 'op' : '=', 'b' : uuh_saasli_id }]
		uuh = request.salesforce_record(uuh_conditions, 'User_Usage_History__c')
		if uuh.sfid is None: # Does this event not already exist?
			uuh_values = {
				'%s__c' % request.triggeringrecordobjecttype : request.triggeringrecord.sfid, #polymorphic relating id
				'User_Usage_History_Event_Type__c' : request.userusagetype.sfid,
				'Event_Date_Created_UNIX__c' : request.eventtime,
				'Saasli_Event_Id__c' : uuh_saasli_id
			}
			return uuh.create(uuh_values) # make the new event
		else:
			logger.error('Event: "{}" already exists.'.format(uuh_saasli_id))
			raise SalesforceError('[400] This event already exists.')
	else:
		logger.error('No triggering object for object: "{}" found.'.format(request.triggeringrecordobjecttype))
		raise SalesforceError('[400] No associating Record found. Ensure the entity that triggered the event already exists in Salesforce.')


def events(event, context):
	return {'Message' : 'Unimplemented'}