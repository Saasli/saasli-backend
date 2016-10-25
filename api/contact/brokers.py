from tools import *

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
		self.error = None

		## Account
		# Get the account values
		try:
			self.accountvalues = self.body['account']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Account Values Specified'})

		# get the account search field
		try:
			a_field = self.path['account']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Account Identifying Field Specified'})

		# Get the search field value
		try:
			a_value = self.accountvalues[a_field]
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Cooresponding Account Identifying Field "%s" Specified' % a_field})

		# Generate the account conditions
		a_conditions = [{ 'a' : a_field, 'op' : '=', 'b' : a_value }]
		self.account = self.salesforce_record(a_conditions, 'Account')

		# There is no account
		if self.account.sfid is None:
			raise SalesforceError({'error' : 'No Account Exists with field: \'%s\' and value: \'%s\'. Saasli requires all contacts to be associated to an Account.' % (a_field, a_value)})

		## Contact
		# Get the contact values
		try:
			self.contactvalues = self.body['contact']
			self.contactvalues.update({'AccountId' : self.account.sfid})
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Contact Values Specified'})

		# Get the contact search field
		try:
			c_field = self.path['contact']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Contact Identifying Field Specified'})

		# Get the search field value
		try:
			c_value = self.contactvalues[c_field]
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Cooresponding Contact Identifying Field "%s" Specified' % c_field})

		# Generate the contact conditions
		c_conditions = [{ 'a' : c_field, 'op' : '=', 'b' : c_value },
						{ 'a' : 'AccountId', 'op' : '=', 'b' : self.account.sfid }] #Make sure we're only getting contacts from the specified account
		self.contact = self.salesforce_record(c_conditions, 'Contact')
