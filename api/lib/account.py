from xml.etree import ElementTree as ET
from Salesforce import SFDC
import logging
import re

log = logging.getLogger()
log.setLevel(logging.DEBUG)

def get_contacts():
	sf_api = SFDC(
		user_name = 'mc@tts.demo', 
		password = 'salesforce3', 
		token = '5ZcOVNre0phV49496kGlhuWw'
	)
	login_response = sf_api.login()
	login_response = ET.fromstring(login_response)

	result_pre_text = '{http://schemas.xmlsoap.org/soap/envelope/}Body/{urn:partner.soap.sforce.com}loginResponse/{urn:partner.soap.sforce.com}result/{urn:partner.soap.sforce.com}'

	try:
		sessionId = login_response[0][0][0][4].text
	except IndexError:
		sys.exit("Error: Salesforce login information may be incorrect")

	instance = login_response.find(result_pre_text + 'metadataServerUrl').text
	instance = re.search('://(.*).salesforce.com', instance)
	instance = instance.group(1)

	sf_api.setSession(instance, sessionId)
	log.debug("Login Success")

	#Get Contacts From Salesforce Where Email is one of the #4 unique emails
	log.debug("Retrieving SF Contacts")
	contacts = sf_api.query_contacts(['hgoddard@saasli.com'])
	sf_contacts = {}
	for contact in contacts:
		sf_contacts[contact['Email']] = contact['Id']
	return sf_contacts