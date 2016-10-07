from account.brokers import AccountRequest
from tools import *


def account(event, context):
	request = AccountRequest(event, context)
	#put the account
	if request.account.sfid is not None:
		return request.account.update(request.accountvalues)
	else:
		return request.account.create(request.accountvalues)

def accounts(event, context):
	return {'Message' : 'Unimplemented'}