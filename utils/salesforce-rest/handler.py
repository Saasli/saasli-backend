import sys, os
sys.path.insert(0, './venv/lib/python2.7/site-packages/') #TODO: Keep an eye out for serverless recognizing venvs and packaging them automatically
from simple_salesforce import Salesforce
import json


def stringify(array):
	out = ""
	for item in array:
		out += ", %s" % item
	return out[1:]


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
	# Auth to Salesforce
	sf = Salesforce(
		username=payload.get('username'), 
		password=payload.get('password'), 
		security_token=payload.get('token')
	)
	# build the query
	query = "SELECT %s FROM %s WHERE %s = '%s' LIMIT 1" % (
		stringify(payload.get('sf_select_fields')),
		payload.get('sf_object_id'), 
		payload.get('sf_field_id'), 
		payload.get('sf_field_value')
	)
	# return the first matching record if it exists, else None
	resp = sf.query(query)
	if (resp.get('totalSize') > 0):
		return resp.get('records')[0]
	else:
		return None