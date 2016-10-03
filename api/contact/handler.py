from contact.brokers import ContactRequest

def contact(event, context):
	request = ContactRequest(event, context)
	#put the contact
	if request.account.exists:
		return request.contact.put(request.contactvalues, request.account.sfid)
	else:
		return {'Error' : 'No such account found'}

def contacts(event, context):
	return { "message": "Go Serverless v1.0! Your function executed successfully!", "event": event }