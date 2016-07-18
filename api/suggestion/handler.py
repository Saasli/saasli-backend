from __future__ import print_function

import json
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)

def handler(event, context):
	log.debug("Received event {}".format(json.dumps(event)))
	response = {}
	if event.get('path') == '/suggestion' and event.get('method') == 'POST':
		if event.get('body') and event.get('body').get('id'):
			body = event.get('body')
			response = get_account(body.get('id'))[0]
		else:
			response['Error'] = "No Body"
	else:
		response['Error'] = "No such endpoint"
	return response