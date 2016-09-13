from tools import KMS
kms = KMS()

def decrypt(payload, context):
	return kms.decrypt(
		payload.get('cipher')
	)

def encrypt(payload, context):
	return kms.encrypt(
		payload.get('key'),
		payload.get('text')
	)