from tools import Microservice
functions = Microservice() # a global instantiation of the boto lambda abstraction

def encrypt(event, context):
	try:
		print event
		payload = { 
			'text' : event.get('body').get('text'),
			'key' : 'alias/clientkey' #todo: figure out how to not hardcode this
		}
		encryptedText = functions.request('kms-dev-encrypt', payload)
		response = {'encrypted' : encryptedText}
	except:
		response = {'Error' : 'Invalid Parameters'}
	return response


def decrypt(event, context):
	try:
		print event
		payload = { 
			'cipher' : event.get('body').get('cipher')
		}
		decryptedText = functions.request('kms-dev-decrypt', payload)
		response = {'decrypted' : decryptedText}
	except:
		response = {'Error' : 'Invalid Parameters'}
	return response