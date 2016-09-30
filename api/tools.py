# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3
import json


class Microservice(object):
	def __init__(self, function_name):
		self.client = boto3.client('lambda')
		self.version = function_name.split('-')[1] #grab the stage name from the function name

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
			print 'No Such Client'

class Request(object):
	def __init__(self, body, path):
		# Assign all the body + path fields to class attributes
		for key, value in body.iteritems():
			setattr(self, key, value)
		# Fish the identifying values out of the json object
		for key, value in path.iteritems():
			print getattr(self, key)
			setattr(self, key + '_field', value)
			setattr(self, key + '_value', getattr(self, key).get(value, None))



	def __iter__(self):
		for attr, value in self.__dict__.iteritems():
			yield attr, value