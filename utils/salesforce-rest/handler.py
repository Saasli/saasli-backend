def get(payload, context):
	print payload
	return { "message": "You called the Salesforce Util!", "back": payload.get('parameter')}
