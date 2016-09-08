# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3
import json
def account(event, context):
	client = boto3.client('lambda')
	payload = json.dumps({'parameter' : 'value'}).encode()
	print payload
	response = json.loads(client.invoke(
		FunctionName='salesforce-dev-get',
		InvocationType='RequestResponse',
		Payload=payload
	)['Payload'].read())
	print response
	message = response.get('message')
	back = response.get('back')
	return { "message from lib": message, "paramter passed through" : back }