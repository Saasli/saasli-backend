# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3
import json

class MissingParameterError(KeyError):
	pass

class AWSError(Exception):
	pass

class CredentialError(Exception):
	pass

class Microservice(object):
	def __init__(self, version):
		self.client = boto3.client('lambda')
		self.version = version

	# Given the name of a lambda function (string) and 
	# a dict containing they {key : value} parameters 
	# returns the response of the lambda function
	def request(self, service, function, payload):
		function_name = "%s-%s-%s" % (service, self.version, function)
		return json.loads( self.client.invoke(
			FunctionName=function_name,
			InvocationType='RequestResponse',
			Payload=json.dumps(payload).encode()
		)['Payload'].read())


#This class expects that stored in the 'credentials' attribute of the client 
#is an encrypted base64 stringified piece of json.
class Credentials(object):
	def __init__(self, id, functions):
		try:
			# Get the encrypted data for the client
			dynamoPayload = {
				'id' : id,
				'key' : 'id',
				'tablename' : 'clients'
			}
			encryptedCredentials = functions.request('dynamodb','getitem', dynamoPayload)
			# Decrypt the client credentials
			kmsPayload = { 
				'cipher' : encryptedCredentials.get('credentials').get('S')
			}
			# Assign all the encrypted fields to class attributes
			for key, value in json.loads(functions.request('kms','decrypt', kmsPayload)).iteritems():
				setattr(self, key, value)
		except:
			raise CredentialError({'error' : 'Invalid Client Id'})


class Request(object):
	def __init__(self, event, context):
		# Get the JSON Body
		try:
			self.body = event['body']
		except KeyError, e:
			return #handle error NO BODY

		# Get the path
		try:
			self.path = event['path']
		except KeyError, e:
			return #handle error NO PATH

		# Get the client id
		try:
			self.clientid = self.body['client_id']
		except KeyError, e:
			return #handle no client id error

		# Get the version of the api
		try:
			self.version = context.function_name.split('-')[1] #grab the stage version name from the function name
		except AttributeError, e:
			return #handle no function name error

		# Get a class instance of lambda microservice
		# TODO Error Handling
		self.functions = Microservice(self.version) # get a class level microservice client

		# Get the SFDC credentials
		# TODO Error Handling
		self.credentials = Credentials(self.clientid, self.functions)


	#returns a new SFRecord
	def get_salesforce_record(self, field, value, object):
		return SFRecord(field, value, object, self.credentials, self.functions)



class SFRecord(object):
	def __init__(self, field, value, object, credentials, functions):
		self.credentials = credentials
		self.functions = functions
		self.object = object
		recordRequest = {
			'sf_object_id' : object, 
			'sf_field_id' : field,
			'sf_field_value' : value,
			'sf_select_fields' : ['Id'] # only interested in the Id
		}
		recordRequest.update(self.credentials.__dict__) #add in the creds
		record = self.functions.request('salesforce-rest', 'get', recordRequest)
		self.exists = record is not None #inform the record exists
		self.sfid = record.get('Id', None)
		print self.sfid

	#run a put on the SFRecord with the appropriate updates
	def put(self, values, sfaccountid=None):
		print "SF ACCOUNT: %s" % sfaccountid
		putPayload = {
			'sf_account_id' : sfaccountid, # Required if it's a contact put TODO: Don't get contact in the first place if it's not part of the account
			'sf_object_id' : self.object, 
			'sf_field_id' : 'Id',
			'sf_field_value' : self.sfid,
			'sf_values' : values
		}
		putPayload.update(self.credentials.__dict__) #add in the creds
		return self.functions.request('salesforce-rest', 'put', putPayload)












