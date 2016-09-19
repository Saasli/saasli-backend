from tools import SalesforceClient

#####
# get
#
# Returns the first record matching the field value
# specified. Should no records match None is 
# returned
#
# @parm
#  payload: dict with the following attributed
#     username - Salesforce username
#     password - Salesforce password
#     token - Salesforce Token
#     sf_object_id - The API Name of the Salesforce Object to query
#     sf_field_id - The API Name of the field holding the query value
#     sf_field_value - The Value of which the first matching occurence is returned
#     sf_select_fields - An array of the API names of the fields to return
#
#  returns e.g.
#    dict
#     {
#         "attributes": {
#             "type": "Contact",
#             "url": "/services/data/v29.0/sobjects/Contact/0031a00000MGU6OAAX"
#         },
#         "Name": "Hank Unspecified",
#         "Id": "0031a00000MGU6OAAX",
#         "AccountId": "0011a00000QwmwcAAB",
#         "Email": "hgoddard@saasli.com"
#     }
#
######

def get(payload, context):
	print payload
	# Auth
	try:
		sf = SalesforceClient(
				payload.get('username'), 
				payload.get('password'), 
				payload.get('token')
			)
	except Exception, e:
		return {'Error' : e.__dict__}
	# Query
	try:
		print "Payload:"
		print payload
		return sf.query(
			payload.get('sf_select_fields'),
			payload.get('sf_object_id'),
			"%s = '%s'" % (payload.get('sf_field_id'), payload.get('sf_field_value'))
		)
	except Exception, e:
		return {"Error" : e.__dict__}

# # For Local Testing Purposes
# print get({
# 	"username" : "mc@tts.demo",
# 	"password" : "salesforce3",
# 	"token" : "5ZcOVNre0phV49496kGlhuWw",
# 	"sf_object_id" : "Contact",
# 	"sf_field_id" : "Phone",
# 	"sf_field_value" : "1800FAKE",
# 	"sf_select_fields" : ['Id', 'Phone', 'Name']
# }, None)
#####
# put
#
# Upserts a new record in salesforce.
#
# @parm
#  payload: dict with the following attributed
#     username - Salesforce username
#     password - Salesforce password
#     token - Salesforce Token
#     sf_values - An object containing a key-value mapping of all the Field API names to values that are to be upserted
#     sf_object_id - The API Name of the Salesforce Object to create a new record for
#     sf_field_id - The API Name of the field holding an identifing id for upsertion
#     sf_field_value - The Identifying Value of which the record will update if found, insert if not
#
#  returns e.g.
#    dict
#     {
#         "Id": "0031a00000MGU6OAAX",
#         "Method": "Created"
#     }
#
######
def put(payload, context):
	print "put"
	# Auth
	try:
		sf = SalesforceClient(
				payload.get('username'), 
				payload.get('password'), 
				payload.get('token')
			)
	except Exception, e:
		return {'Error' : e.__dict__}
	# Query
	try:
		#generate where clause
		where = "%s = '%s'" % (payload.get('sf_field_id'), payload.get('sf_field_value'))
		# in the case of a contact, make sure their accountid is considered, and only update those who match
		if payload.get('sf_object_id') == 'Contact':
			try:
				where += " AND AccountId = '%s'" % payload['sf_account_id'] #pass this value in as sf_account_id
				print "ADDING ACCOUNT TO WHERE %s" % where
			except Exception, e:
				return {"Error", "Account Id invalid"}

		#execute the query
		exists = sf.query(
			['Id'],
			payload.get('sf_object_id'),
			where
		)
	except Exception, e:
		return {'Error' : e.__dict__}
	# Upsert
	if exists is not None: #do an update if it exists
		try:
			update_result = sf.update(exists.get('Id'), payload.get('sf_object_id'), payload.get('sf_values'))
			return {"Method" : "Update", "Id" : exists.get('Id')}
		except Exception, e:
			return {"Error" : e.__dict__}
	else: #create it if not
		try:
			#add the identifying key/value pair as a value upon creation (unless it's the Record Id... don't do that)
			values = payload.get('sf_values')
			if payload.get('sf_field_id') is not "Id":
				values.update({
					payload.get('sf_field_id') : payload.get('sf_field_value')
				})

			create_result = sf.create(payload.get('sf_object_id'), values)
			return {"Method" : "Create", "Id" : create_result.get('id')}
		except Exception, e:
			return {"Error" : e.__dict__}

# # For Local Testing Purposes
# print put({
# 	"username" : "mc@tts.demo",
# 	"password" : "salesforce3",
# 	"token" : "5ZcOVNre0phV49496kGlhuWw",
# 	"sf_object_id" : "Account",
# 	"sf_field_id" : "Name",
# 	"sf_field_value" : "Test Update Identifying",
# 	"sf_values" : {
# 		"Phone" : "1800GOTJUNK"
# 	}
# }, None)