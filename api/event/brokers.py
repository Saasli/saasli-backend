from tools import *


#little tool to turn an array into a field query string
def stringify(array):
    out = ""
    for item in array:
        out += ", '%s'" % item
    return out[1:] #greasy skip the first comma
# Expecting to see 
# Body
# {
#     "client_id" : "saasli",
#     "account" : {
#     	"Name" : "ACME"	
#     },
#     "contact" : {
#         "LastName" : "Waites",
#         "FirstName" : "Tom",
#         "Phone" : "+1 123 123 1234"
#     }
# }
# Path
# {
# 	"account" : "Name"
# 	"contact" : "Phone"
# }

class EventRequest(Request):
	def __init__(self, event, context):
		# Instantiate the base request
		Request.__init__(self, event, context)

		## Triggering Object
		# Get the triggering object type
		try:
			self.triggeringrecordobjecttype = self.body['sf_object_id']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Type Specified'})

		# get the object search field
		try:
			triggeringrecordfield = self.body['sf_field_id']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Identifying Field Specified'})

		# Get the search field value
		try:
			triggeringrecordvalue = self.body['sf_field_value']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Cooresponding Account Identifying Field "%s" Specified' % triggeringrecordfield})

		# Get event name
		try:
			self.eventname = self.body['event']['event_name']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Event Name Specified'})


		# Get event timestamp
		try:
			self.eventtime = self.body['event']['event_timestamp']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Event Time Specified'})

		# OPTIONAL PARAMS
		# Additional Event Values
		try:
			self.eventvalues = self.body['event'].get('event_values')
		except Exception, e:
			raise Exception({'error' : 'Issues with optional parameters'})

		# Specified Saasli Event Id
		try: 
			self.eventid = self.body['event'].get('event_id')
		except Exception, e:
			raise Exception({'error' : 'Issues with optional parameters'})


		# Get the triggering record (if it exists)
		r_conditions = [{ 'a' : triggeringrecordfield, 'op' : '=', 'b' : triggeringrecordvalue }]
		self.triggeringrecord = self.salesforce_record(r_conditions, self.triggeringrecordobjecttype)

		# get the user usage history type record (if it exists)
		uuhet_conditions = [{ 'a' : 'Name', 'op' : '=', 'b' : self.eventname }]
		self.userusagetype = self.salesforce_record(uuhet_conditions, 'User_Usage_History_Event_Type__c')
		# if the UUH type doesn't exist, make it
		if self.userusagetype.sfid is None:
			self.userusagetype.create({'Name' : self.eventname})

class EventsRequest(Request):
	def __init__(self, event, context):
		# Instantiate the base request
		Request.__init__(self, event, context)

		## Triggering Object
		# Get the triggering object type
		try:
			self.triggeringrecordobjecttype = self.body['sf_object_id']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Type Specified'})

		# get the object search field
		try:
			self.triggeringrecordfield = self.body['sf_field_id']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Identifying Field Specified'})

		# Get the search field value
		try:
			self.eventsarray = self.body['events']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Events Array Specified'})

		# pick out unique uuhet names
		try:
			eventnames = []
			i = 0
			for event in self.eventsarray:
				if event['event']['event_name'] not in eventnames:
					logger.info('Event: {}'.format(event))
					eventnames.append(event['event']['event_name'])
					i += 1
		except KeyError, e:
			logger.error('Error: {}'.format(e))
			raise MissingParameterError({'error' : "Event {} Malformed in Event Array".format(str(i))})
		logger.info('Unique Events: {}'.format(eventnames))

		# get the uuhet id's for the unique event names
		try:
			uuhet_conditions = [{
					'a' : 'Name',
					'op' : 'IN',
					'b' : '({})'.format(stringify(eventnames))
			}]
			uuhet_payload = { 'sf_object_id' : 'User_Usage_History_Event_Type__c', 'sf_select_fields' : ['Name', 'Id'], 'sf_conditions' : uuhet_conditions }
			uuhet_payload.update(self.credentials.__dict__)
			logger.info('Unique Events Payload: {}'.format(uuhet_payload))
			uuhet_id_results = self.functions.request('salesforce-bulk', 'get', uuhet_payload)["results"]
			logger.info('Unique Events Payload Results: {}'.format(uuhet_id_results))
		except Exception, e:
			raise Exception({ "error" : "Couldn't Get the UUHET SFIDs"})

		# confirm that all the required uuhet's exist
		try:
			uuhet_mappings = {} #create an existing name:id uuhet mapping
			for uuhet_record in uuhet_id_results:
				if (uuhet_record['Name'] in eventnames):
					uuhet_mappings.update({uuhet_record['Name'] : uuhet_record['Id']})
					eventnames.remove(uuhet_record['Name']) #remove the matched event name from the list
		except Exception, e:
			raise Exception({"error" : "Error Mapping User Usage History Event Type Names: {}".format(e)})

		# create the leftover uuhet's
		try:
			new_uuhet_records = []
			for uuhet_name in eventnames:
				new_uuhet_records.append({'Name' : uuhet_name})
			new_uuhet_payload = { 'sf_object_id' : 'User_Usage_History_Event_Type__c', 'sf_records' : new_uuhet_records }
			new_uuhet_payload.update(self.credentials.__dict__)
			logger.info('Create New Events Payload: {}'.format(new_uuhet_payload))
			new_uuhet_id_results = self.functions.request('salesforce-bulk', 'create', new_uuhet_payload)["results"]
			logger.info('Create New Events Payload Results: {}'.format(new_uuhet_id_results))
		except Exception, e:
			raise Exception({ "error" : "Error Creating the new Event Types: {} Error: {}".format(eventnames, e)})

		# add the newly created uuhet's to the uuhet_mappings
		try:
			# NOTE: I'm running under the assumption that the results are in the same order as the insertion request. If not, we'll have to perform yet another query.
			for new_uuhet_record in new_uuhet_id_results:
				uuhet_mappings.update({eventnames[0] : new_uuhet_record['id']}) #Creations return lowercase 'id'
				eventnames.pop(0) #delete the 0th name for the next iteration.
		except Exception, e:
			raise Exception({"error" : "Error Mapping New User Usage History Event Type Names: {}".format(e)})

