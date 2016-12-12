from tools import *


#little tool to turn an array into a field query string
def stringify(array):
    out = ""
    for item in array:
        out += ", {}".format(item) if isnum(item) else ", '{}'".format(item) #Don't wrap integers in quotes
    return out[1:] #greasy skip the first comma

#is the str actually an int?
def isnum(str):
	try:
		float(str)
		return True
	except:
		return False

class QueryTree(object):
    def __init__(self, lookupobjs, functions, credentials):
    	self.functions
    	self.credentials
        self.tree = {}
        for lookupobj in lookupobjs:
            self.processLookup(lookupobj)
        self.generateQueries()
        self.getSFDCIds()

    def processLookup(self, lookupobj):
        obj, field, value = lookupobj['object'], lookupobj['field'], lookupobj['unique_value']
        if obj not in self.tree.keys():
            self.tree[obj] = {} #make the new object dict

        if field not in self.tree[obj].keys():
            self.tree[obj][field] = [] #make the new field array

        if value not in self.tree[obj][field]:
            self.tree[obj][field].append(value)

    def generateQueries(self):
        queries = []
        for obj in self.tree.keys():
            selectclause, fromclause, whereclause = '', '', 'WHERE '
            fields = self.tree[obj].keys()
            if 'Id' not in self.tree[obj].keys(): #make sure that the Id is one of the requested fields
                fields.append('Id')

            for field in self.tree[obj].keys():
                whereclause += '{} IN ({}) OR '.format(field, self.stringify(self.tree[obj][field]))
            whereclause = whereclause[:-5]
            selectclause = 'SELECT {}'.format(self.stringify(fields, False))
            fromclause = 'FROM {}'.format(obj)
            self.tree[obj]['query'] = '{} {} {}'.format(selectclause, fromclause, whereclause)
        return self.tree

    def getSFDCIds(self):
        for obj in self.tree.keys():
            query_payload = { 'sf_query' : self.tree[obj]['query'] }
            query_payload.update(self.credentials.__dict__)
            print self.functions('salesforce-rest', 'query', query_payload)


    #little tool to turn an array into a field query string
    def stringify(self, array, applyquotes=True):
        out = ""
        print applyquotes
        for item in array:
            out += ", {}".format(item) if (self.isnum(item) or not applyquotes) else ", '{}'".format(item) #Don't wrap integers in quotes
        return out[2:] #greasy skip the first comma

    #is the str actually an int?
    def isnum(self, str):
        try:
            float(str)
            return True
        except:
            return False

class ObjectsRequest(Request):
	def __init__(self, event, context):
		# Instantiate the base request
		Request.__init__(self, event, context)

		# Get the object type
		try:
			self.objecttype = self.path['object']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Type Specified (sf_object_id)'})

		# get the object external id field
		try:
			self.upsertfield = self.path['external_id_field']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Triggering Object Identifying Field Specified (sf_field_id)'})

		# Get the objects
		try:
			self.objectsarray = self.body['objects']
		except KeyError, e:
			raise MissingParameterError({'error' : 'No Objects Array Specified (objects)'})


		####
		# 1) Lookup Objects
		#
		# Get the SFIDs of all the lookup records in the objects array
		####

		# a) pick out all fields representing a lookup field
		try:
			lookupobjects = []
			i = 0
			for objectrecord in self.objectsarray: #iterate through all the objects
				for field in objectrecord.keys(): #iterate through all the object keys
					if (type(objectrecord[field]) is dict): #check for instances of obj (means a lookup)
						lookupobjects.append(objectrecord[field]) #add to all the lookups
				i += 1
		except KeyError, e:
			logger.error('Error: {}'.format(e))
			raise MissingParameterError({'error' : "Object {} Malformed in Object Array".format(str(i))})

		# b) manufacture a data structure to hold all the records we're going to query for the lookups
		try:
			querytree = QueryTree(lookupobjects, self.functions)
		except Exception, e:
			raise Exception({"error" : "Query Tree Failed to generate: {}".format(e)})
		

		# c) 

		####
		# 2) Triggering Objects
		#
		# Get the salesforce records that are to be associated to
		# each of the events
		####

		# a) get the triggering records to be associated from SFDC (using list from 1b))
		try:
			triggering_records_conditions = [{
					'a' : self.triggeringrecordfield,
					'op' : 'IN',
					'b' : '({})'.format(stringify(fieldvalues))
			}]
			triggering_records_payload = { 'sf_object_id' : self.triggeringrecordobjecttype, 'sf_select_fields' : [self.triggeringrecordfield, 'Id'], 'sf_conditions' : triggering_records_conditions }
			triggering_records_payload.update(self.credentials.__dict__)
			logger.info('Triggering Record Payload: {}'.format(triggering_records_payload))
			triggering_records_id_results = self.functions.request('salesforce-bulk', 'get', triggering_records_payload)["results"]
			logger.info('Triggering Record Payload Results: {}'.format(triggering_records_id_results))
		except Exception, e:
			raise Exception({ "error" : "Couldn't Get the triggering records: {}".format(e)})

		# b) confirm that all the triggering records do exist
		try:
			self.triggering_records_mappings = {} #create a mapping of sf_field_value:Id for each event
			if isinstance(fieldvalues[0], basestring): #if we're dealing with string identifiers we need to be a bit more careful
				fieldvalues_lower = map(unicode.lower,fieldvalues) #clone a lowercase version for matching purposes
				for triggering_record in triggering_records_id_results:
					if (triggering_record[self.triggeringrecordfield].lower() in fieldvalues_lower): #It is possible for SFDC to return matchs with different cases. We'll compare case insensitive
						index = fieldvalues_lower.index(triggering_record[self.triggeringrecordfield].lower()) #get the index in the lowercase list of the matching fieldvalue
						self.triggering_records_mappings.update({fieldvalues[index] : triggering_record['Id']})
						fieldvalues.pop(index) #get rid of the matched element from the fieldvalues
						fieldvalues_lower.pop(index) #also apply to it's lowercase clone
			else: #otherwise we need not worry about case, and treat normally
				for triggering_record in triggering_records_id_results:
					if (triggering_record[self.triggeringrecordfield] in fieldvalues): 
						index = fieldvalues.index(triggering_record[self.triggeringrecordfield])
						self.triggering_records_mappings.update({fieldvalues[index] : triggering_record['Id']})
						fieldvalues.pop(index) #get rid of the matched element from the fieldvalues

			print self.triggering_records_mappings
		except Exception, e:
			raise Exception({"error" : "Error Mapping User Usage History Event Type Names: {}".format(e)})

		#TODO: Offer the ability to create new associating records should they not exist here.

























