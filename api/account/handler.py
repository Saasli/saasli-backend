from __future__ import print_function

import json
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

def handler(event, context):
	log.debug("Received event {}".format(json.dumps(event)))
	log.debug("Received context %s" % context)
	response = {}
	if event.get('path') == '/account' and event.get('method') == 'GET':
		response['route'] = "GET"
		log.debug("Received GET")
	elif event.get('path') == '/account/create' and event.get('method') == 'POST':
		log.debug("Received /create POST")
		response['route'] = "POST"
	else:
		response['error'] = "No such endpoint"
	return response
