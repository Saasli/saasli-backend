from __future__ import print_function

import sys, os

import json
import logging
from src.suggestions import get_suggestions

log = logging.getLogger()
log.setLevel(logging.DEBUG)

def get_request_params(event):
	try:
		return event.get('path'), event.get('body'), event.get('method')
	except:
		return -1

def handler(event, context):
	log.debug("HANDLER Path: {}".format(os.path.abspath(os.path.join(os.path.dirname(__file__)))))
	log.debug("Received event {}".format(json.dumps(event)))
	response = {}
	if event.get('path') == '/suggestion' and event.get('method') == 'POST':
		if event.get('body') and event.get('body').get('PushTopic'):
			try:
				pushtopic = event.get('body').get('PushTopic')
				sfid = event.get('body').get('sobject').get('Id')
				log.debug("Id is {}".format(sfid))
				log.debug("PushTopic is {}".format(pushtopic))
				get_suggestions(sfid)
			except:
				response['Error'] = "No PushTopic or Id specified"

			response['Success'] = "Ok"
		else:
			response['Error'] = "No Body"
	else:
		response['Error'] = "No such endpoint"
	return response