# Thank you http://stackoverflow.com/questions/36784925/how-to-get-return-response-from-aws-lambda-function
import boto3

class KMS(object):
	def __init__(self):
		self.client = boto3.client('kms')

	def encrypt(self, text):
		#Decrypt
		return True

	#NOTE: unlike 'encrypt', no key_id is actually needed. AWS just determines if you have the rights to access it,
	# and if so, it decrypts it.
	def decrypt(self, cipher):
		response = self.client.decrypt(
			CiphertextBlob=cipher,
			#EncryptionContext={ 'string': 'string' },
			GrantTokens=[ 'string' ]
		)
		return response.get('Plaintext').decode('UTF-8')