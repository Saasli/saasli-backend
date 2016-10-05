# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3
import json

class MissingParameterError(KeyError):
	pass

class SalesforceError(Exception):
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
			raise CredentialError('400 Invalid Client Id')


class Request(object):
	def __init__(self, event, context):
		# Get the JSON Body
		try:
			self.body = event['body']
		except KeyError, e:
			raise MissingParameterError({"error", "400 No Body"})

		# Get the path
		try:
			self.path = event['path']
		except KeyError, e:
			raise MissingParameterError({"error", "400 No Path"})

		# Get the client id
		try:
			self.clientid = self.body['client_id']
		except KeyError, e:
			raise MissingParameterError({'error' : '400 No Client Id'})

		# Get the version of the api
		try:
			self.version = context.function_name.split('-')[1] #grab the stage version name from the function name
		except AttributeError, e:
			raise AWSError({'error' : '500 Fatal Error'})

		# Get a class instance of lambda microservice
		try:
			self.functions = Microservice(self.version) # get a class level microservice client
		except:
			raise AWSError({"error" : self.functions})

		# Get the SFDC credentials
		self.credentials = Credentials(self.clientid, self.functions)


	#returns a new SFRecord
	def salesforce_record(self, conditions, object):
		return SFRecord(conditions, object, self.credentials, self.functions)

class SFRecord(object):
	def __init__(self, conditions, object, credentials, functions):
		self.credentials = credentials
		self.functions = functions
		self.object = object
		self.sfid = self.get(conditions)['Id'] if self.get(conditions) is not None else None #Get the sfid or None
	
	def get(self, conditions):
		getPayload = {
			'sf_object_id' : self.object, 
			'sf_conditions' : conditions,
			'sf_select_fields' : ['Id'] # only interested in the Id
		}
		getPayload.update(self.credentials.__dict__) #add in the creds
		getResponse = self.functions.request('salesforce-rest', 'get', getPayload)
		if not getResponse['error']:
			return getResponse['response']
		else:
			raise SalesforceError(getResponse['message'])

	#run a put on the SFRecord with the appropriate updates
	def put(self, values):
		putPayload = {
			'sf_object_id' : self.object, 
			'sf_field_id' : 'Id',
			'sf_field_value' : self.sfid,
			'sf_values' : values
		}
		putPayload.update(self.credentials.__dict__) #add in the creds
		response = self.functions.request('salesforce-rest', 'put', putPayload)
		self.sfid = response['Id'] #make sure the sfid is up to date
		return response

	#run a create on the SFRecord with the appropriate updates
	def create(self, values):
		createPayload = {
			'sf_object_id' : self.object, 
			'sf_values' : values
		}
		createPayload.update(self.credentials.__dict__) #add in the creds
		response = self.functions.request('salesforce-rest', 'create', createPayload)
		self.sfid = response['id'] #make sure the sfid is up to date
		return response

	#run an update on the SFRecord with the appropriate updates
	def update(self, values):
		updatePayload = {
			'sf_object_id' : self.object, 
			'sf_id' : self.sfid,
			'sf_values' : values
		}
		updatePayload.update(self.credentials.__dict__) #add in the creds
		print updatePayload
		return self.functions.request('salesforce-rest', 'update', updatePayload)








