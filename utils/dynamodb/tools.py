import boto3

class DynamoDB(object):
	def __init__(self):
		self.client = boto3.client('dynamodb')

	def get_item(self, tablename, key, value):
		response = client.get_item(
			TableName=tablename,
			Key={ key: { 'S': value } }
		)
		return response.get('Item')
