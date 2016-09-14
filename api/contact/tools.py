# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3
import json

class Microservice(object):
	def __init__(self):
		self.client = boto3.client('lambda')

	# Given the name of a lambda function (string) and 
	# a dict containing the {key : value} parameters 
	# returns the response of the lambda function
	def request(self, function, payload):
		return json.loads( self.client.invoke(
			FunctionName=function,
			InvocationType='RequestResponse',
			Payload=json.dumps(payload).encode()
		)['Payload'].read())


#This class expects that stored in the 'credentials' attribute of the client 
#is an encrypted base64 stringified piece of json.
class Credentials(object):
	def __init__(self, id):
		try:
			functions = Microservice()
			# Get the encrypted data for the client
			dynamoPayload = {
				'id' : id,
				'key' : 'id',
				'tablename' : 'clients'
			}
			encryptedCredentials = functions.request('dynamodb-dev-getitem', dynamoPayload)
			# Decrypt the client credentials
			kmsPayload = { 
				'cipher' : encryptedCredentials.get('credentials').get('S')
			}
			# Assign all the encrypted fields to class attributes
			for key, value in json.loads(functions.request('kms-dev-decrypt', kmsPayload)).iteritems():
				setattr(self, key, value)
		except:
			print 'No Such Client'