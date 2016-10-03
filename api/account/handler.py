from account.brokers import AccountRequest

#Expecting a payload as defined here: https://saasli.github.io/docs/#account
def account(event, context):
	request = AccountRequest(event, context)
	#put the account
	return request.account.put(request.accountvalues)

def accounts(event, context):
	return {'Message' : 'Unimplemented'}