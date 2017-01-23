from tools import DynamoDB
dynamodb = DynamoDB()

def getitem(payload, context):
    return dynamodb.get_item(
        payload.get('tablename'), 
        payload.get('key'), 
        payload.get('id')
    )


def updateitem(payload, context):
    return dynamodb.update_item(
        payload.get('tablename'),
        payload.get('key'),
        payload.get('id'),
        payload.get('updateexpression'),
        payload.get('expressionattributevalues')
    )