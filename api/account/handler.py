from account.brokers import AccountRequest
from tools import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def account(event, context):
	logger.info('account endpoint hit: {}'.format(event))
	request = AccountRequest(event, context)
	#put the account
	if request.account.sfid is not None:
		logger.info('Account does exist: performing update')
		return request.account.update(request.accountvalues)
	else:
		logger.info('Account does not exist: performing create')
		return request.account.create(request.accountvalues)

def accounts(event, context):
	return {'Message' : 'Unimplemented'}