import hashlib
from event.brokers import EventRequest, EventsRequest
from tools import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_hash(identifier_sf_id, logged_at):
	join = str(identifier_sf_id) + str(logged_at)
	hash = hashlib.md5(join)
	return hash.hexdigest()


def event(event, context):
	logger.info('event endpoint hit: {}'.format(event))
	request = EventRequest(event, context)

	if request.triggeringrecord.sfid is not None: # Do we have a record to associate this too?
		logger.info('Creating new event.')

		if request.eventid is None: # If there isn't a saasli event id specified, we'll manufacture a unique one
			logger.info('No Event Id Provided, Generating Id.')
			request.eventid = generate_hash(request.triggeringrecord.sfid, request.eventtime)

		uuh_conditions = [{ 'a' : 'Saasli_Event_Id__c', 'op' : '=', 'b' : request.eventid }]
		uuh = request.salesforce_record(uuh_conditions, 'User_Usage_History__c')
		uuh_values = {
			'%s__c' % request.triggeringrecordobjecttype : request.triggeringrecord.sfid, #polymorphic relating id
			'User_Usage_History_Event_Type__c' : request.userusagetype.sfid,
			'Event_Date_Created_UNIX__c' : request.eventtime,
			'Saasli_Event_Id__c' : request.eventid
		}
		if request.eventvalues is not None:
			uuh_values.update(request.eventvalues)

		if uuh.sfid is None: # Does this event not already exist?
			return uuh.create(uuh_values) # make the new event
		else: #update the event
			return uuh.update(uuh_values)
	else:
		logger.error('No triggering object for object: "{}" found.'.format(request.triggeringrecordobjecttype))
		raise SalesforceError('[400] No associating Record found. Ensure the entity that triggered the event already exists in Salesforce.')


def events(event, context):
    logger.info('event endpoint hit: {}'.format(event))
    request = EventsRequest(event, context)
    return "Thanks"
    #return functions.request('salesforce-bulk','create', payload)