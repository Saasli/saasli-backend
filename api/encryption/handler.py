import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))) # we need to add the parent directory to the path so we can share tools.py
from tools import Microservice

def encrypt(event, context):
	functions = Microservice(context.function_name.split('-')[1])
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
	functions = Microservice(context.function_name.split('-')[1])
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