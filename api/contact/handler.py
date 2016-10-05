from contact.brokers import ContactRequest
from tools import *

def contact(event, context):
	try:
		request = ContactRequest(event, context)
	except MissingParameterError as e:
		return e.args[0]
	except CredentialError as e:
		return e.args[0]
	except AWSError as e:
		return e.args[0]

	#try and get the account
	if request.account.sfid is not None:
		#put the contact
		if request.contact.sfid is not None:
			return request.contact.update(request.contactvalues)
		else:
			return request.contact.create(request.contactvalues)
	else:
		return {'error' : 'No such account found'}

def contacts(event, context):
	return { "message": "Go Serverless v1.0! Your function executed successfully!", "event": event }