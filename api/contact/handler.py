from contact.brokers import ContactRequest
from tools import *

def contact(event, context):
	request = ContactRequest(event, context)

	#try and get the account
	if request.account.sfid is not None:
		#put the contact
		if request.contact.sfid is not None:
			return request.contact.update(request.contactvalues)
		else:
			return request.contact.create(request.contactvalues)
	else:
		raise SalesforceError('[400] No associating Account found.')

def contacts(event, context):
	return { "message": "Go Serverless v1.0! Your function executed successfully!", "event": event }