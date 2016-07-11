from __future__ import print_function

import json
import logging
import sys, os
# sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../")) #required for access to lib functions
# import lib
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))
sys.path.append(os.path.join(here, "./lib"))
sys.path.append(os.path.join(here, "../../vendored"))
sys.path.append(os.path.join(here, "../../lib"))

log = logging.getLogger()
log.setLevel(logging.DEBUG)

import Salesforce

log.debug("After import")

def handler(event, context):
	log.debug("Received event {}".format(json.dumps(event)))
	log.debug("Received context %s" % context)
	response = {}
	if event.get('path') == '/account' and event.get('method') == 'GET':
		response['route'] = "GET"
		log.debug("Received GET")
	elif event.get('path') == '/account/create' and event.get('method') == 'POST':
		log.debug("Received /create POST")
		response = get_contacts()
	else:
		response['error'] = "No such endpoint"
	return response



#handler({ "path": "/account/create", "method": "POST" }, '')


