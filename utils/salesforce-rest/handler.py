import sys, os
sys.path.insert(0, './venv/lib/python2.7/site-packages/') #TODO: Keep an eye out for serverless recognizing venvs and packaging them automatically
from simple_salesforce import Salesforce, SFType
import json

#little tool to turn an array into a field query string
def stringify(array):
	out = ""
	for item in array:
		out += ", %s" % item
	return out[1:]

#grants a sf client if authorization is successful
def auth(username, password, security_token):
	try:
		# Auth to Salesforce
		return Salesforce(
			username=, 
			password=payload.get('password'), 
			security_token=payload.get('token')
		)
	except:
		return None

#perform a sf query
def query(query_string, sf):
	try:
		# return the first matching record if it exists, else None
		resp = sf.query(query_string)
		if (resp.get('totalSize') > 0):
			return resp.get('records')[0]
		else:
			return None
	except:
		print "Salesforce Query Failed: %s" % query_string
		return None



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
	sf = auth(payload.get('username'), payload.get('password'), payload.get('token'))
	if sf is not None:
		# build the query
		query_string = "SELECT %s FROM %s WHERE %s = '%s' LIMIT 1" % (
			stringify(payload.get('sf_select_fields')),
			payload.get('sf_object_id'), 
			payload.get('sf_field_id'), 
			payload.get('sf_field_value')
		)
		return query(query_string, sf)
	else:
		return sf

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
#     sf_object_id - The API Name of the Salesforce Object to create a new record for
#     sf_field_id - The API Name of the field holding an identifing id for upsertion
#     sf_field_value - The Identifying Value of which the record will update if found, insert if not
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

def post(payload, context):
	sf = auth(payload.get('username'), payload.get('password'), payload.get('token'))
	if sf is not None:
		# check if the record exists
		query_string = "SELECT Id FROM %s WHERE %s = '%s' LIMIT 1" % (
			payload.get('sf_object_id'), 
			payload.get('sf_field_id'), 
			payload.get('sf_field_value')
		)
		upsert = query(query_string)
		if (upsert is not None): #This record exists! We're doing an update
			objectType = SFType(upsert.get('attribute').get('type'),'sesssionid','na1.salesforce.com')


	else:
		return sf