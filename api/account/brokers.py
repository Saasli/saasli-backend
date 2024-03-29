from tools import *

# Expecting to see 
# Body
# {
#     "client_id" : "ad2d965b-57d9-4943-a879-c2a33d9a857b",
#     "account" : {
#         "Name" : "ACME",
#         "Id" : "0011a00000DlaOMAAZ"
#     }
# }
# Path
# {
# 	"account" : "Name"
# }

class AccountRequest(Request):
	def __init__(self, event, context):
		# Instantiate the base request
		Request.__init__(self, event, context)
		# Get Account Specific Details

		# Get the account values
		try:
			self.accountvalues = self.body['account']
		except KeyError, e:
			raise MissingParameterError({'error' : '400 Missing Account Values'})

		# Get the search field
		try:
			field = self.path['account']
		except KeyError, e:
			raise MissingParameterError({'error' : '400 No Account Identifying Field Specified'})

		# Get the search field value
		try:
			value = self.accountvalues[field]
		except KeyError, e:
			raise MissingParameterError({'error' : '400 No Cooresponding Account Identifying Field "%s" Specified' % field})

		conditions = [{ 'a' : field, 'op' : '=', 'b' : value }]
		self.account = self.salesforce_record(conditions, 'Account')
