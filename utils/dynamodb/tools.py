import boto3

class DynamoDB(object):
    def __init__(self):
        self.client = boto3.client('dynamodb')

    def get_item(self, tablename, key, value):
        response = self.client.get_item(
            TableName=tablename,
            Key={ key: { 'S': value } }
        )
        return response.get('Item')

    def update_item(self, tablename, key, value, updateexpression, expressionattributevalues):
        print key
        print updateexpression
        print expressionattributevalues
        return self.client.update_item(
            TableName=tablename,
            Key={ key: { 'S': value } },
            UpdateExpression=updateexpression,
            ExpressionAttributeValues=expressionattributevalues
        )
