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
		print function_name
		return json.loads( self.client.invoke(
			FunctionName=function_name,
			InvocationType='RequestResponse',
			Payload=json.dumps(payload).encode()
		)['Payload'].read())