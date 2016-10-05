from tools import *

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

		# Get the triggering record (if it exists)
		r_conditions = [{ 'a' : triggeringrecordfield, 'op' : '=', 'b' : triggeringrecordvalue }]
		self.triggeringrecord = self.salesforce_record(r_conditions, self.triggeringrecordobjecttype)

		# get the user usage history record (if it exists)
		uuhet_conditions = [{ 'a' : 'Name', 'op' : '=', 'b' : self.eventname }]
		self.userusagetype = self.salesforce_record(uuhet_conditions, 'User_Usage_History_Event_Type__c')
		# if the UUH type doesn't exist, make it
		if self.userusagetype.sfid is None:
			self.userusagetype.create({'Name' : self.eventname})





















