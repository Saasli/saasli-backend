from tools import Request

# Expecting to see 
# Body
# {
#     "client_id" : "saasli",
#     "account" : {
#     	"Name" : "ACME"	
#     },
#     "contact" : {
#         "LastName" : "Waites",
#         "FirstName" : "Tom",
#         "Phone" : "+1 123 123 1234"
#     }
# }
# Path
# {
# 	"account" : "Name"
# 	"contact" : "Phone"
# }

class ContactRequest(Request):
	def __init__(self, event, context):
		# Instantiate the base request
		Request.__init__(self, event, context)

		## Account
		# Get the account values
		try:
			self.accountvalues = self.body['account']
		except KeyError, e:
			return #handle error NO account param

		# get the account search field
		try:
			a_field = self.path['account']
		except KeyError, e:
			return #handle no account param specified

		# Get the search field value
		try:
			a_value = self.accountvalues[a_field]
		except KeyError, e:
			return #handle error NO id value param

		self.account = self.get_salesforce_record(a_field, a_value, 'Account')


		## Contact
		# Get the contact values
		try:
			self.contactvalues = self.body['contact']
		except KeyError, e:
			return #handle error NO contact param

		# Get the contact search field
		try:
			c_field = self.path['contact']
		except KeyError, e:
			return #handle no contact param specified

		# Get the search field value
		try:
			c_value = self.contactvalues[c_field]
		except KeyError, e:
			return #handle error NO id value param

		self.contact = self.get_salesforce_record(c_field, c_value, 'Contact')
