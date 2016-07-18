from __future__ import print_function

import json
import logging
from account import get_account

log = logging.getLogger()
log.setLevel(logging.DEBUG)


def handler(event, context):
	log.debug("Received event {}".format(json.dumps(event)))
	log.debug("Received context %s" % context)
	response = {}
	if event.get('path') == '/account' and event.get('method') == 'POST':
		if event.get('body') and event.get('body').get('id'):
			body = event.get('body')
			print("Data: {}".format(json.dumps(event.get('data'))))
			response = get_account(body.get('id'))[0]
		else:
			response['Error'] = "No Body"
	else:
		response['Error'] = "No such endpoint"
	return response

#handler({ "path": "/account/create", "method": "POST" }, '')