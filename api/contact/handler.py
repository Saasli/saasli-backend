from contact.brokers import ContactRequest
from tools import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def contact(event, context):
	logger.info('contact endpoint hit: {}'.format(event))
	request = ContactRequest(event, context)
	#try and get the account
	if request.account.sfid is None:
		#put the contact
		if request.contact.sfid is not None:
			logger.info('Contact does exist: performing update')
			return request.contact.update(request.contactvalues)
		else:
			logger.info('Contact does not exist: performing create')
			return request.contact.create(request.contactvalues)
	else:
		logger.error('No such account exists to associate contact')
		raise SalesforceError('[400] No associating Account found.')

def contacts(event, context):
	return { "message": "Go Serverless v1.0! Your function executed successfully!", "event": event }