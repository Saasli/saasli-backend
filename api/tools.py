# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
		logger.info('Requesting. {}'.format(function_name))
		response = json.loads( self.client.invoke(
			FunctionName=function_name,
			InvocationType='RequestResponse',
			Payload=json.dumps(payload).encode()
		)['Payload'].read())
		logger.info('Raw Response. {}'.format(response))
		if (response is not None and response.get('errorType', False)): # Is there an errorType (handle None value case)? 
			logger.info('Response Failed: {}'.format(response))
			response.pop('stackTrace', None) # Get rid of the stackTrace
			raise Exception(response['errorMessage']) # Throw the error out to the client
		else:
			logger.info('Response Successful: {}'.format(response))
			return response


#This class expects that stored in the 'credentials' attribute of the client 
#is an encrypted base64 stringified piece of json.
class Credentials(object):
	def __init__(self, id, functions):
		logger.info('Obtaining Salesforce Credentials.')
		# Get the encrypted data for the client
		dynamoPayload = {
			'id' : id,
			'key' : 'id',
			'tablename' : 'clients'
		}
		encryptedCredentials = functions.request('dynamodb','getitem', dynamoPayload)
		
		if encryptedCredentials is None:
			raise CredentialError({'error' : 'client id not found'}) #Take a look to see if the client id was found or not

		logger.info('Retrieved Encrypted Credentials Successfully.')
		# Decrypt the client credentials
		kmsPayload = { 
			'cipher' : encryptedCredentials.get('credentials').get('S')
		}
		# Assign all the encrypted fields to class attributes
		decryptedCredentials = functions.request('kms','decrypt', kmsPayload)['Plaintext']
		logger.info('Decrypted Credentials Successfully.')
		for key, value in json.loads(decryptedCredentials).iteritems():
			logger.info('Adding Attribute {}:{} to Credentials Class.'.format(key, value))
			setattr(self, key, value)


class Request(object):
	def __init__(self, event, context):
		logger.info('Processing Request.')
		# Get the JSON Body
		try:
			self.body = event['body']
		except KeyError, e:
			raise MissingParameterError({"error", "[400] No Body"})

		# Get the path
		try:
			self.path = event['path']
		except KeyError, e:
			raise MissingParameterError({"error", "[400] No Path"})

		# Get the client id
		try:
			self.clientid = self.body['client_id']
		except KeyError, e:
			raise MissingParameterError({'error' : '[400] No Client Id'})

		# Get the version of the api
		try:
			self.version = context.function_name.split('-')[1] #grab the stage version name from the function name
			logger.info('API Version: {}'.format(self.version))
		except AttributeError, e:
			raise AWSError({'error' : '[500] Fatal Error'})

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
		logger.info('Initializing New SF Record Class: {}.'.format(object))
		self.credentials = credentials
		self.functions = functions
		self.object = object
		self.sfid = self.get(conditions)['Id']
	
	def get(self, conditions):
		logger.info('SF Record Get: {}.'.format(self.object))
		getPayload = {
			'sf_object_id' : self.object, 
			'sf_conditions' : conditions,
			'sf_select_fields' : ['Id'] # only interested in the Id
		}
		getPayload.update(self.credentials.__dict__) #add in the creds
		return self.functions.request('salesforce-rest', 'get', getPayload)
			

	#run a put on the SFRecord with the appropriate updates
	def put(self, values):
		logger.info('SF Record Put: {}.'.format(self.object))
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
		logger.info('SF Record Create: {}.'.format(self.object))
		createPayload = {
			'sf_object_id' : self.object, 
			'sf_values' : values
		}
		createPayload.update(self.credentials.__dict__) #add in the creds
		response = self.functions.request('salesforce-rest', 'create', createPayload)
		self.sfid = response['Id'] #make sure the sfid is up to date
		return response

	#run an update on the SFRecord with the appropriate updates
	def update(self, values):
		logger.info('SF Record Update: {}.'.format(self.object))
		updatePayload = {
			'sf_object_id' : self.object, 
			'sf_id' : self.sfid,
			'sf_values' : values
		}
		updatePayload.update(self.credentials.__dict__) #add in the creds
		print updatePayload
		return self.functions.request('salesforce-rest', 'update', updatePayload)








