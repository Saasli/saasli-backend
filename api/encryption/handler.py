from tools import Microservice

def encrypt(event, context):
	functions = Microservice(context.function_name)
	try:
		print event
		payload = { 
			'text' : event.get('body').get('text'),
			'key' : 'alias/clientkey' #todo: figure out how to not hardcode this
		}
		encryptedText = functions.request('kms', 'encrypt', payload)
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
		decryptedText = functions.request('kms', 'decrypt', payload)
		response = {'decrypted' : decryptedText}
	except:
		response = {'Error' : 'Invalid Parameters'}
	return response