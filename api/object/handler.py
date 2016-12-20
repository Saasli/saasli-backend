import hashlib
from object.brokers import ObjectsRequest
from tools import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_hash(identifier_sf_id, logged_at):
    join = str(identifier_sf_id) + str(logged_at)
    hash = hashlib.md5(join)
    return hash.hexdigest()


def objects(event, context):
    logger.info('objects endpoint hit: {}'.format(event))
    request = ObjectsRequest(event, context)

    if len(request.records) > 0: #if there are no records to upsert, don't bother trying
        # Manufacture the payload destined for salesforce-bulk
        upsert_payload = { 
            'sf_object_id' : request.object,
            'sf_records' : request.records,
            'external_id' : request.externalId
        }
        upsert_payload.update(request.credentials.__dict__)
        response = request.functions.request('salesforce-bulk', 'upsert', upsert_payload) # Fire the request
    
    return({'Success' : True})