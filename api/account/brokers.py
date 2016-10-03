from tools import Request

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
# 	"account" : "Phone"
# 	"contact" : "Name"
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
			return #handle error NO account param

		# Get the search field
		try:
			field = self.path['account']
		except KeyError, e:
			return #handle no account param specified

		# Get the search field value
		try:
			value = self.accountvalues[field]
		except KeyError, e:
			return #handle error NO account param

		self.account = self.get_salesforce_record(field, value, 'Account')
