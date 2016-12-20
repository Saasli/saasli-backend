from tools import *

'''
Class to facilitate mapping of lookup fields to actual SFDC Ids
'''
class QueryTree(object):
    def __init__(self, objectsarray, functions, credentials):
        self.objectsarray = objectsarray
        self.functions = functions
        self.credentials = credentials
        self.tree = {}
        self.lookupobjects = []
        self.lookupExtraction() #extract all the fields representing lookups into an instance array
        self.processLookups() #take the passed lookup field declarations and fit them to the tree
        self.generateQueries() #generate one query per lookup object
        self.getSFDCIds() #retrieve the SFDC Ids of the lookup objects

    '''
    lookupExtraction(self)
    ----------------------
    Given an array of records to be inserted into Salesforce, extract those representing
    lookups, and store in an instance array.
    '''
    def lookupExtraction(self):
        for objectrecord in self.objectsarray: #iterate through all the objects
            for field in objectrecord.keys(): #iterate through all the object keys
                if (type(objectrecord[field]) is dict): #check for instances of obj (means a lookup)
                    self.lookupobjects.append(objectrecord[field]) #add to all the lookups

    '''
    processLookup(self, lookupobj)
    ------------------------------
    Takes an array of the form:

    lookupobjects = [
        {
            "Object" : "objectname",
            "Field" : "fieldname",
            "Value": "value"
        },
        {
            "Object" : "objectname",
            "Field" : "fieldname",
            "Value": "value"
        },
        {
            "Object" : "objectname",
            "Field" : "fieldname",
            "Value": "value"
        },
        {
            "Object" : "objectname",
            "Field" : "fieldname",
            "Value": "value"
        },
        {
            "Object" : "objectname",
            "Field" : "fieldname",
            "Value": "value"
        },
    ]

    And generates a tree of the form:

    {
        'Object' : {
            'Field': {
                {'Value' : None},
                {'Value' : None},
                {'Value' : None}
            },
            'Field': {
                {'Value' : None},
            }
        },
        'Object' : {
            'Field': {
                {'Value' : None},
                {'Value' : None},
                {'Value' : None}
            }
        },
    }
    '''
    def processLookups(self):
        for lookupobj in self.lookupobjects:
            obj, field, value = lookupobj['object'], lookupobj['field'], lookupobj['unique_value']
            if obj not in self.tree.keys():
                self.tree[obj] = {} #make the new object dict

            if field not in self.tree[obj].keys():
                self.tree[obj][field] = {} #make the new field object

            if value not in self.tree[obj][field].keys():
                self.tree[obj][field][value] = None #add a placeholder for the SFDC id to be mapped

    '''
    generateQueries(self)
    ---------------------
    Creates a S(O)QL query for each object in the tree. Ensuring that
    Each field and Id is returned with the appropriate values in the Where
    clause. The query is stored in an attribute of each object in the tree.
    '''
    def generateQueries(self):
        queries = []
        for obj in self.tree.keys():
            selectclause, fromclause, whereclause = '', '', 'WHERE '
            fields = self.tree[obj].keys()
            if 'Id' not in self.tree[obj].keys(): #make sure that the Id is one of the requested fields
                fields.append('Id')

            for field in self.tree[obj].keys():
                whereclause += '{} IN ({}) OR '.format(field, self.stringify(self.tree[obj][field].keys()))
            whereclause = whereclause[:-4]
            selectclause = 'SELECT {}'.format(self.stringify(fields, False))
            fromclause = 'FROM {}'.format(obj)
            self.tree[obj]['query'] = '{} {} {}'.format(selectclause, fromclause, whereclause)
        return self.tree

    '''
    getSFDCIds(self)
    -----------------
    Uses the querys created in generateQueries(self) and attempts to match as many
    Salesforce records as possible. The matching SFDC Ids are stored in the tree as the
    value cooresponding to each key in each Field object. Anything not matched will
    remain 'None' like this:
    {
        'Object' : {
            'Field': {
                {'Value' : 0011a00000DlaOWEAZ},
                {'Value' : None},
                {'Value' : 0011a00000Dlr4MAAZ}
            },
            'Field': {
                {'Value' : 0011a00000Dla3YAAZ},
            }
        },
        'Object' : {
            'Field': {
                {'Value' : None},
                {'Value' : 0011a00000DlaOMIAZ},
                {'Value' : 0011a00000DleOPAAZ}
            }
        },
    }
    '''
    def getSFDCIds(self):
        for obj in self.tree.keys(): #perform for each object in tree
            query_payload = { 'sf_query' : self.tree[obj].pop('query') } #take the query out of the tree and put into a payload
            query_payload.update(self.credentials.__dict__)
            results = self.functions.request('salesforce-rest', 'query', query_payload) #query the results
            if results.get('totalSize') > 0:
                for field in self.tree[obj].keys():
                    for value in self.tree[obj][field].keys():
                        matching = next((record for record in results['records'] if record[field] == value), None) #get the matching record's Id
                        if matching is not None:
                            self.tree[obj][field][value] = matching['Id']

    '''
    getMatchedObjectsArray(self)
    ----------------------------
    A method to return an array with fields representing lookups changed
    to actual SFDC Ids they are denoting. NOTE: Removes any instances of null or None
    '''
    def getMatchedObjectsArray(self):
        for i, objectrecord in enumerate(self.objectsarray): #enumerate through all the objects
            for field in objectrecord.keys(): #iterate through all the object keys
                if (type(objectrecord[field]) is dict): #check for instances of obj (means a lookup)
                    o, f, v = objectrecord[field]['object'], objectrecord[field]['field'], objectrecord[field]['unique_value']
                    sfdcid = self.tree[o][f][v]
                    if sfdcid is not None:
                        objectrecord[field] = self.tree[o][f][v] #return the cooresponding Id from the tree
                    else:
                        del self.objectsarray[i][field] #get rid of the lookup if it doesn't exist
                elif (objectrecord[field] is None):
                    del self.objectsarray[i][field] #get rid of any null fields
        return self.objectsarray


    #little tool to turn an array into a field query string
    def stringify(self, array, applyquotes=True):
        out = ""
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
            self.object = self.path['object']
        except KeyError, e:
            raise MissingParameterError({'error' : 'No Object Type Specified (object) in URL path'})

        # get the object external id field
        try:
            self.externalId = self.path['external_id']
        except KeyError, e:
            raise MissingParameterError({'error' : 'No Object External Id Field Specified (external_id) in URL path'})

        # Get the objects
        try:
            self.objectsarray = self.body['records']
        except KeyError, e:
            raise MissingParameterError({'error' : 'No Objects Array Specified (records) in body'})

        # Match all the lookup representations with actual SFDC Ids
        try:
            self.records = QueryTree(self.objectsarray, self.functions, self.credentials).getMatchedObjectsArray()
        except Exception, e:
            raise Exception({"error" : "Unable to associate lookups, malformed records array: {}".format(e)})






