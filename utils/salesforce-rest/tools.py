import sys
sys.path.insert(0, './venv/lib/python2.7/site-packages/') #TODO: Keep an eye out for serverless recognizing venvs and packaging them automatically
from simple_salesforce import Salesforce, SFType
import json


#a local representation of the SF Client's Object
class SalesforceObject(object):
	def __init__(self, object, session_id, sf_instance):
		self.sf_type = SFType(object, session_id, sf_instance)
		self.description = self.sf_type.describe()
		self.fields = self.description['fields']
		self.typemap = {
			'address' : True,
			'anyType' : True,
			'boolean' : True,
			'calculated' : True,
			'combobox' : True,
			'currency' : False,
			'double' : False,
			'DataCategoryGroupReference' : True,
			'email' : True,
			'encryptedstring' : True,
			'id' : True,
			'JunctionIdList' : True,
			'location' : True,
			'masterrecord' : True,
			'multipicklist' : True,
			'percent' : False,
			'phone' : True,
			'picklist' : True,
			'reference' : True,
			'string' : True,
			'textarea' : True,
			'url' : True,
		} # True -> Do put quotes
		# False -> Do not put quotes

	def getFieldType(self, fieldname):
		x = [fields['type'] for fields in self.fields if fields['name'] == fieldname][0]
		print x
		return x

	def formatFieldType(self, fieldname, value):
		if self.typemap.get(self.getFieldType(fieldname)):
			return "'%s'" % value
		else:
			return "%s" % value



class SalesforceClient(object):
	#grants a sf client if authorization is successful
	def __init__(self, username, password, token):
		self.sf = Salesforce(
			username=username, 
			password=password, 
			security_token=token
		)
		self.session_id = self.sf.session_id
		self.sf_instance = self.sf.sf_instance

	#little tool to turn an array into a field query string
	def stringify(self, array):
		out = ""
		for item in array:
			out += ", %s" % item
		return out[1:] #greasy skip the first comma

	#perform a sf query (SELECT only)
	# where is an array of dicts where each dict contains the left and right terms as well as the operation between the two
	# e.g. 
	# {
	#   a : 'Id',
	#   b : 'WxThsThdDUs000AAT',
	#  op : '='
	# }
	def query(self, columns, table, where, limit=1):
		query_string = "SELECT %s FROM %s WHERE %s LIMIT %s" % (self.stringify(columns), table, where, limit)
		print ("QS: %s" % query_string)
		# return the first matching record if it exists, else None
		resp = self.sf.query(query_string)
		if (resp.get('totalSize') > 0):
			return resp.get('records')[0]
		else:
			return None

	#create a new record of type 'object' with values of type dict
	def create(self, object_type, values):
		sf_type = SFType(object_type, self.session_id, self.sf_instance)
		return sf_type.create(values)

	#update and existing record given it's sf_id
	def update(self, sf_id, object_type, values):
		sf_type = SFType(object_type, self.session_id, self.sf_instance)
		return sf_type.update(sf_id, values)