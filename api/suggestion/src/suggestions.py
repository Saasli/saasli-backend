from __future__ import print_function

import sys, os
import json
import logging
import re
import time
import datetime
from xml.etree import ElementTree as ET

# OS Path Hack to import modules from the common directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))) # /var/task
sys.path.insert(0, './common')

log = logging.getLogger()
log.setLevel(logging.DEBUG)
from Salesforce import SFDC



def get_suggestions(sfid):
	#login
	sf_api = SFDC(
		user_name = os.environ['SFDC_USER'], 
		password = os.environ['SFDC_PASSWORD'], 
		token = os.environ['SFDC_TOKEN']
	)

	login_response = sf_api.login()
	login_response = ET.fromstring(login_response)
	log.debug("Login Response Dict {}".format(login_response))

	result_pre_text = '{http://schemas.xmlsoap.org/soap/envelope/}Body/{urn:partner.soap.sforce.com}loginResponse/{urn:partner.soap.sforce.com}result/{urn:partner.soap.sforce.com}'

	try:
		sessionId = login_response[0][0][0][4].text
		log.debug("SessionId {}".format(sessionId))
	except IndexError:
		log.debug("Failed Login")
		sys.exit("Error: Salesforce login information may be incorrect")

	instance = login_response.find(result_pre_text + 'metadataServerUrl').text
	instance = re.search('://(.*).salesforce.com', instance)
	instance = instance.group(1)
	log.debug("Instance: {}".format(instance))

	sf_api.setSession(instance, sessionId)
	log.debug("Login Success")

	#query the account
	account = sf_api.query(["Id", "Name"], "Account")
	log.debug("Response: {}".format(account))
	
	#query suggestions
	log.debug("Response: {}".format(sf_api.query_suggestion(sfid)))





