from tools import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Takes the payload an returns an sfclient
def auth(payload):
    # Auth
    return BulkSalesforce(
        username=payload['username'], 
        password=payload['password'], 
        token=payload['token'], 
        version=36.0, #Default to 36.0 for now
        sandbox=payload['sandbox']
    )

# Query Payload
# payload = {
#     "username" : "mc@tts.demo",
#     "password" : "salesforce4",
#     "token" : "3y5J5a9lKjzZ0lhFVEgutEmkd",
#     "sandbox" : True,
#     "sf_object_id" : "Account",
#     "sf_select_fields" : ['Id', 'Name'],
#     "sf_conditions" : [{
#         "a" : "Name",
#         "op" : "=",
#         "b" : "Acme 2"
#     }]
# }
#print sf.query("Account", "SELECT Id, Name FROM Account LIMIT 10")
def get(payload, context):
    sf = auth(payload)
    response = sf.query(
        payload['sf_object_id'],
        payload['sf_select_fields'],
        payload['sf_conditions']
    )
    return {"results" : response if response is not None else []} #toss back an empty array instead of just 'None'


# # Insert Payload
# payload = {
#     "username" : "mc@tts.demo",
#     "password" : "salesforce4",
#     "token" : "3y5J5a9lKjzZ0lhFVEgutEmkd",
#     "sandbox" : True,
#     "sf_object_id" : "Account",
#     "sf_records" : [
#         {
#             "Name" : "New Account Henry",
#             "description" : "yo"
#         },
#         {
#             "Name" : "New Account Henry 2",
#             "description" : "yo"
#         }
#     ]
# }
def create(payload, context):
    sf = auth(payload)
    return {"results" : sf.insert(
        payload['sf_object_id'],
        payload['sf_records']
    )}


# # Update Payload
# payload = {
#     "username" : "mc@tts.demo",
#     "password" : "salesforce4",
#     "token" : "3y5J5a9lKjzZ0lhFVEgutEmkd",
#     "sandbox" : True,
#     "sf_select_fields" : ['Id', 'Name'],
#     "sf_records" : [
#         {
#             "Name" : "New Account Henry **UPDATE",
#             "description" : "yo",
#             "Id" : "0011a00000YRfSmAAL"
#         },
#         {
#             "Name" : "New Account Henry 2 **UPDATE",
#             "description" : "yo",
#             "Id" : "0011a00000YRfSnAAL"
#         }
#     ]
# }

def update(payload, context):
    sf = auth(payload)
    return {"results" : sf.update(
        payload['sf_object_id'],
        payload['sf_records']
    )}

def upsert(payload, context):
    sf = auth(payload)
    return {"results" : sf.upsert(
        payload['sf_object_id'],
        payload['sf_records'],
        payload['external_id']
    )}






