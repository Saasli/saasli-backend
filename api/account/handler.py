from account.brokers import AccountRequest
from tools import *

def account(event, context):
	try:
		request = AccountRequest(event, context)
	except MissingParameterError as e:
		return e.args[0]
	except CredentialError as e:
		return e.args[0]
	except AWSError as e:
		return e.args[0]

	#put the account
	if request.account.sfid is not None:
		return request.account.update(request.accountvalues)
	else:
		return request.account.create(request.accountvalues)

def accounts(event, context):
	return {'Message' : 'Unimplemented'}