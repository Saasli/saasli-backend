from tools import *


#little tool to turn an array into a field query string
def stringify(array):
    out = ""
    for item in array:
        out += ", {}".format(item) if isnum(item) else ", '{}'".format(item) #Don't wrap integers in quotes
    return out[1:] #greasy skip the first comma

#is the str actually an int?
def isnum(str):
	try:
		float(str)
		return True
	except:
		return False
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
			raise MissingParameterError({'error' : 'No Triggering Object Type Specified (sf_object_id)'})

		# get the object search field
		try:
			self.triggeringrecordfield = self.body['sf_field_id']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Identifying Field Specified (sf_field_id)'})

		# get the event lookup id
		try:
			self.triggeringlookupfield = self.body['sf_lookup_id']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Lookup Field on Event Record Specified (sf_lookup_id)'})

		# Get the events
		try:
			self.eventsarray = self.body['events']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Events Array Specified (events)'})


		####
		# 1) User Usage History Event Types (UUHET)
		#
		# Get and create as necessary, the SFIDs of the UUHET
		# records that will be needed to create the events
		####

		# a) pick out unique uuhet names
		# b) create list of sf_field_values as well
		try:
			eventnames = []
			fieldvalues = []
			i = 0
			for event in self.eventsarray:
				if event['event']['event_name'] not in eventnames:
					logger.info('Event: {}'.format(event))
					eventnames.append(event['event']['event_name'])
				if event['sf_field_value'] not in fieldvalues:
					logger.info('Field Value: {}'.format(event))
					fieldvalues.append(event['sf_field_value'])
				i += 1
		except KeyError, e:
			logger.error('Error: {}'.format(e))
			raise MissingParameterError({'error' : "Event {} Malformed in Event Array".format(str(i))})
		logger.info('Unique Events: {}'.format(eventnames))

		# c) get the uuhet id's for the unique event names from SFDC
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
			raise Exception({ "error" : "Couldn't Get the UUHET SFIDs: {}".format(e)})

		# d) confirm that all the required uuhet's exist
		try:
			self.uuhet_mappings = {} #create an existing name:id uuhet mapping
			for uuhet_record in uuhet_id_results:
				if (uuhet_record['Name'] in eventnames):
					self.uuhet_mappings.update({uuhet_record['Name'] : uuhet_record['Id']})
					eventnames.remove(uuhet_record['Name']) #remove the matched event name from the list
		except Exception, e:
			raise Exception({"error" : "Error Mapping User Usage History Event Type Names: {}".format(e)})

		if len(eventnames) > 0: #If there are some unmatched event names, we need to make them in SFDC
			logger.info('Creating New Events')
		# e) create the leftover uuhet's
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

		# f) add the newly created uuhet's to the self.uuhet_mappings
			try:
				# NOTE: I'm running under the assumption that the results are in the same order as the insertion request. If not, we'll have to perform yet another query.
				for new_uuhet_record in new_uuhet_id_results:
					self.uuhet_mappings.update({eventnames[0] : new_uuhet_record['id']}) #Creations return lowercase 'id'
					eventnames.pop(0) #delete the 0th name for the next iteration.
			except Exception, e:
				raise Exception({"error" : "Error Mapping New User Usage History Event Type Names: {}".format(e)})
		else:
			logger.info('All Events Exist, No New Events Required.')

		####
		# 2) Triggering Objects
		#
		# Get the salesforce records that are to be associated to
		# each of the events
		####

		# a) get the triggering records to be associated from SFDC (using list from 1b))
		try:
			triggering_records_conditions = [{
					'a' : self.triggeringrecordfield,
					'op' : 'IN',
					'b' : '({})'.format(stringify(fieldvalues))
			}]
			triggering_records_payload = { 'sf_object_id' : self.triggeringrecordobjecttype, 'sf_select_fields' : [self.triggeringrecordfield, 'Id'], 'sf_conditions' : triggering_records_conditions }
			triggering_records_payload.update(self.credentials.__dict__)
			logger.info('Triggering Record Payload: {}'.format(triggering_records_payload))
			triggering_records_id_results = self.functions.request('salesforce-bulk', 'get', triggering_records_payload)["results"]
			logger.info('Triggering Record Payload Results: {}'.format(triggering_records_id_results))
		except Exception, e:
			raise Exception({ "error" : "Couldn't Get the triggering records: {}".format(e)})

		# b) confirm that all the triggering records do exist
		try:
			self.triggering_records_mappings = {} #create a mapping of sf_field_value:Id for each event
			if isinstance(fieldvalues[0], basestring): #if we're dealing with string identifiers we need to be a bit more careful
				fieldvalues_lower = map(unicode.lower,fieldvalues) #clone a lowercase version for matching purposes
				for triggering_record in triggering_records_id_results:
					if (triggering_record[self.triggeringrecordfield].lower() in fieldvalues_lower): #It is possible for SFDC to return matchs with different cases. We'll compare case insensitive
						index = fieldvalues_lower.index(triggering_record[self.triggeringrecordfield].lower()) #get the index in the lowercase list of the matching fieldvalue
						self.triggering_records_mappings.update({fieldvalues[index] : triggering_record['Id']})
						fieldvalues.pop(index) #get rid of the matched element from the fieldvalues
						fieldvalues_lower.pop(index) #also apply to it's lowercase clone
			else:
				for triggering_record in triggering_records_id_results:
					if (triggering_record[self.triggeringrecordfield] in fieldvalues): 
						index = fieldvalues.index(triggering_record[self.triggeringrecordfield])
						self.triggering_records_mappings.update({fieldvalues[index] : triggering_record['Id']})
						fieldvalues.pop(index) #get rid of the matched element from the fieldvalues

			print self.triggering_records_mappings
		except Exception, e:
			raise Exception({"error" : "Error Mapping User Usage History Event Type Names: {}".format(e)})

		#TODO: Offer the ability to create new associating records should they not exist here.

























