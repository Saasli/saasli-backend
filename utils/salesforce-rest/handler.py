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
	sf = SalesforceClient(payload.get('username'), payload.get('password'), payload.get('token'))
	if sf is not None:
		# build the query
		query_string = "SELECT %s FROM %s WHERE %s = '%s' LIMIT 1" % (
			stringify(payload.get('sf_select_fields')),
			payload.get('sf_object_id'), 
			payload.get('sf_field_id'), 
			payload.get('sf_field_value')
		)
		#print sf.create(payload.get('sf_object_id'), payload.get('sf_values'))
		return sf.query(query_string)
	else:
		return None

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
	sf = SalesforceClient(payload.get('username'), payload.get('password'), payload.get('token'))
	if sf is not None:
		# build the query to find if a specified object exists
		query_string = "SELECT %s FROM %s WHERE %s = '%s' LIMIT 1" % (
			'Id',
			payload.get('sf_object_id'), 
			payload.get('sf_field_id'), 
			payload.get('sf_field_value')
		)
		exists = sf.query(query_string)
		if exists is not None: #do an update if it exists
			updated = sf.update(exists.get('Id'), payload.get('sf_object_id'), payload.get('sf_values'))
			print "%s Exists, updated %s" % (payload.get('sf_field_value'), exists.get('Id'))
			return {"Id" : exists.get('Id'), "Method" : "Update"}
		else: #create it if not
			created = sf.create(payload.get('sf_object_id'), payload.get('sf_values'))
			print "%s Does Not Exist, created %s" % (payload.get('sf_field_value'), created.get('id'))
			return {"Id" : created.get('id'), "Method" : "Create"}
	else:
		return None

# For Local Testing Purposes
# put({
# 	"username" : "mc@tts.demo",
# 	"password" : "salesforce3",
# 	"token" : "5ZcOVNre0phV49496kGlhuWw",
# 	"sf_object_id" : "Contact",
# 	"sf_field_id" : "Email",
# 	"sf_field_value" : "hgoddard+new@saasli.com",
# 	"sf_values" : {
# 		"Email" : "hgoddard+new@saasli.com",
# 		"LastName" : "Hank88"
# 	}
# }, None)