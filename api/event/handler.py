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
	sf_records = [] #instantiate the array holding all the objects for upsert
	i = 0 # keep a count of this procedure for error clarity
	
	# Build the sf_records array for bulk upsertion
	for event in request.eventsarray:
		record = {} # instantiate the record
		
		try:
			# See if the triggering record id exists
			triggering_record_id = request.triggering_records_mappings.get(event['sf_field_value'])
			
			if triggering_record_id is not None: # If there isn't a record to associate it to, then we're done here.
				# Set the triggering record id
				try:
					record.update({'{}__c'.format(request.triggeringrecordobjecttype) : triggering_record_id}) #Set the Polymorphic relating triggering record id
				except Exception, e:
					raise MissingParameterError({'error' : 'Missing or Malformed \'sf_field_value\' in event {}'.format(i)})

				# Set the Saasli_Event_Id__c
				try:
					if event['event'].get("event_id") is None: # we'll make out own hash and use it as an id
						event_id = generate_hash(triggering_record_id, event['event']['event_timestamp'])
					else: # let's use the id specified
						event_id = event['event']['event_id']
					record.update({'Saasli_Event_Id__c' : event_id})
				except Exception, e:
					raise MissingParameterError({'error' : 'Malformed \'event_id\' in event {}'.format(i)})
				
				# Set the UUHET
				try:
					record.update( {'User_Usage_History_Event_Type__c' : request.uuhet_mappings[event['event']['event_name']] })
				except Exception, e:
					raise MissingParameterError({'error' : 'Missing or Malformed \'event_name\' in event {}'.format(i)})

				# Set the Event Time
				try:
					record.update({'Event_Date_Created_UNIX__c' : event['event']['event_timestamp']})
				except Exception, e:
					raise MissingParameterError({'error' : 'Missing or Malformed \'event_timestamp\' in event {}'.format(i)})

				# Set any additional values (if included)
				try:
					if event['event'].get('event_values') is not None:
						record.update(event['event']['event_values'])
				except Exception, e:
					raise MissingParameterError({'error' : 'Malformed \'event_values\' in event {}. Ensure values are a list of Salesforce API Names to Value pairs.'.format(i)})

				sf_records.append(record) #append the formatted record to the sf_records list
		except Exception, e:
			logger.info('Skipping Event {} for error {}'.format(i, e))
			pass
		i += 1 # increment the event counter

	events_payload = { 
		'sf_object_id' : 'User_Usage_History__c', # inserting into the User Usage History Object
		'sf_records' : sf_records,
		'external_id' : 'Saasli_Event_Id__c'
	}

	events_payload.update(request.credentials.__dict__)
	print json.dumps(events_payload, indent=4)
	return request.functions.request('salesforce-bulk', 'upsert', events_payload)


    	
















