import boto3
import json

class Microservice(object):
	def __init__(self):
		self.client = boto3.client('lambda')

	# Given the name of a lambda function (string) and 
	# a dict containing they {key : value} parameters 
	# returns the response of the lambda function
	def request(self, function, payload):
		return json.loads( self.client.invoke(
			FunctionName=function,
			InvocationType='RequestResponse',
			Payload=json.dumps(payload).encode()
		)['Payload'].read())