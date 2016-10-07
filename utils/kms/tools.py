import boto3
import base64

class KMS(object):
	def __init__(self):
		self.client = boto3.client('kms')

	#NOTE: Serverless can't serialize the byte stream that encrypt returns
	#so we base64 encode it.
	def encrypt(self, key, text):
		response = self.client.encrypt(
			KeyId=key,
			Plaintext=text
		)['CiphertextBlob'] = base64.b64encode(response.get('CiphertextBlob')) #base64 encode the blob
		return response

	def decrypt(self, cipher):
		response = self.client.decrypt(
			CiphertextBlob=base64.b64decode(cipher),
		)
		return response