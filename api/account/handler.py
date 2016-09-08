from lib.test import hey

def account(event, context):
	return { "message from lib": hey("Henry") }
