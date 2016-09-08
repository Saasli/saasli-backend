# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3
import json
def account(event, context):
	client = boto3.client('lambda')
	response = client.invoke(
		FunctionName='salesforce-dev-get',
		InvocationType='RequestResponse'
		#Payload=b'bytes'|file,
	)
	message = json.loads(response['Payload'].read()).get('message')
	return { "message from lib": message }