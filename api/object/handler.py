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
	return({'Success' : True})