import boto3, json, logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
		if response.get('errorType', False): # Is there an errorType? 
			logger.info('Response Failed: {}'.format(response))
			response.pop('stackTrace', None) # Get rid of the stackTrace
			raise Exception(response['errorMessage']) # Throw the error out to the client
		else:
			logger.info('Response Successful: {}'.format(response))
			return response

class DatabaseCredentials(object):
	def __init__(self, id, functions):
		logger.info('Obtaining Client Database Credentials.')
		# Get the encrypted data for the client
		dynamoPayload = {
			'id' : id,
			'key' : 'id',
			'tablename' : 'clients'
		}
		encryptedCredentials = functions.request('dynamodb','getitem', dynamoPayload)
		logger.info('Retrieved Encrypted Database Credentials Successfully.')
		# Decrypt the client credentials
		kmsPayload = { 
			'cipher' : encryptedCredentials.get('database').get('S')
		}
		# Assign all the encrypted fields to class attributes
		decryptedCredentials = functions.request('kms','decrypt', kmsPayload)['Plaintext']
		logger.info('Decrypted Credentials Successfully.')
		for key, value in json.loads(decryptedCredentials).iteritems():
			logger.info('Adding Attribute {}:{} to DatabaseCredentials Class.'.format(key, value))
			setattr(self, key, value)