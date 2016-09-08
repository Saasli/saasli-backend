# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3

class KMS(object):
	def __init__(self):
		self.client = boto3.client('kms')

	def encrypt(self, text):
		#Decrypt
		return True

	def decrypt(self, cipher):
		#Encrypt
		return True