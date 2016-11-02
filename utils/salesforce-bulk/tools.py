import sys
sys.path.insert(0, './venv/lib/python2.7/site-packages/') #TODO: Keep an eye out for serverless recognizing venvs and packaging them automatically
import time, json, urllib, urllib2, requests, re, logging #for sending requests
from simple_salesforce import SFType
from xml.etree import ElementTree as ET
#Squelch the annoying certificate errors
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


#Thanks http://stackoverflow.com/questions/2148119/how-to-convert-an-xml-string-to-a-dictionary-in-python
class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    print "here?"
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)

class XmlDictConfig(dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                else:
                    aDict = {re.sub('{.*?}','',element[0].tag) : XmlListConfig(element)}
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({re.sub('{.*?}','',element.tag): aDict})
            elif element.items():
                self.update({re.sub('{.*?}','',element.tag): dict(element.items())}) # re.sub('{.*?}','',element.tag) gets rid of the curlies
            else:
                self.update({re.sub('{.*?}','',element.tag): element.text})


class BulkSalesforce(object):
    def __init__(self, username, password, token, sandbox, version=36.0):
        self.username = username # SFDC Username
        self.password = password # SFDC Password
        self.token = token # The SFDC Login Token
        self.version = version # The Bulk API Version 36.0 is the default
        self.sandbox = sandbox # Important for determining if the login is to Sandbox or Prod
        self.login() # Perform the XML Login

    #TODO: Key an eye on Salesforce supporting json logins
    def login(self):
        # Generate the login url and request
        loginUrl = "https://{}.salesforce.com/services/Soap/u/{}".format("test" if self.sandbox else "login", self.version)
        loginRequest = u"""<?xml version="1.0" encoding="utf-8" ?>
        <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
            <env:Body>
                <n1:login xmlns:n1="urn:partner.soap.sforce.com">
                    <n1:username>""" + self.username + """</n1:username>
                    <n1:password>""" + self.password + self.token + """</n1:password>
                </n1:login>
            </env:Body>
        </env:Envelope>""".encode('utf-8')
        # Establish the login headers
        headers = {
            "Content-Type": "text/xml; charset=UTF-8",
            "SOAPAction": "login"
        }
        # Fire the login                      
        response = requests.post(
            url=loginUrl,
            headers = headers,
            data = loginRequest,
            verify=False
        )
        print response.text
        # Extract the session, serverUrl and instance
        try:
            tree = ET.fromstring(response.text)
            result = XmlDictConfig(tree)['Body']['loginResponse']['result'] #Get the response as a dict
            self.sessionId = result['sessionId']
            self.serverUrl = result['serverUrl']
            self.instance = re.search('://(.*).salesforce.com', self.serverUrl).group(1)
            return
        except Exception, e:
            print "Login Failed {}".format(e)

    #little tool to turn a where dict in to a properly formatted where string in a query string
    def whereify(self, array, object):
        out = ""
        for clause in array:
            if clause['op'] == "IN": #If the op type is 'IN' we don't want to wrap our array in quotes.
                out += "AND %s %s %s " % (clause['a'], clause['op'], clause['b'])
            else:
                out += "AND %s %s %s " % (clause['a'], clause['op'], "{}".format(clause['b']) if self.isnum(clause['b']) else "'{}'".format(clause['b'])) 
        return out[4:] #greasy first AND skip

    #little tool to turn an array into a field query string
    def stringify(self, array):
        out = ""
        for item in array:
            out += ", %s" % item
        return out[1:] #greasy skip the first comma

    def isnum(self, str):
        try:
            float(str)
            return True
        except:
            return False

    def create_job(self, operation, object):
        # Using Composition, give the current instance to the job
        return BulkSalesforceJob(self, operation, object)

    def query(self, object, columns, where, chunksize=0):
        try:
            query_string = "SELECT %s FROM %s WHERE %s" % (self.stringify(columns), object, self.whereify(where, object))
        except Exception, e:
            raise Exception("Malformed Query {}".format(e))

        try:
            query_job = BulkSalesforceJob(self, "query", object, chunksize=chunksize)
        except Exception, e:
            raise Exception("Unable to Create Salesforce Job {}".format(e))

        try:
            query_job.create_batch(query_string)
        except Exception, e:
            raise Exception("Unable to Create Salesforce Batch {}".format(e))

        # This is going to only support 100,000 Rows, to properly PK chunk we need https://success.salesforce.com/issues_view?id=a1p300000008ZL6AAM
        try:
            # Wait for the job to finish
            status = query_job.batches[0].get_status()
            while (status["state"] != "Completed"):
                if status["state"] == "Failed":
                    query_job.close_job() #TODO: Build an abort
                    return
                print "Query Status: {}".format(status["state"])
                status = query_job.batches[0].get_status()
                time.sleep(1)
            results = query_job.batches[0].get_query_results()
            query_job.close_job()
            return results

        except Exception, e:
            print "Query Failure: {}".format(e)

    def insert(self, object, rows, chunksize=10000):
        try:
            insert_job = BulkSalesforceJob(self, "insert", object, chunksize=chunksize)
            total_rows = len(rows)
            print "Creating {}/{}={} chunks".format(total_rows, chunksize, total_rows / chunksize)
        except Exception, e:
            raise Exception("Unable to Create Salesforce Job: {}".format(e))
        
        try:
            for i in range(0, total_rows, chunksize):
                insert_job.create_batch(rows[i:i + chunksize])
        except Exception, e:
            raise Exception("Unable to Create Salesforce Batch: {}".format(e))

        try:
            # Wait for the last batch to finish
            status = insert_job.batches[-1].get_status()
            while (status["state"] != "Completed"):
                print "Insert Status: {}".format(status["state"])
                status = insert_job.batches[-1].get_status()
                time.sleep(1)
            results = []
            for batch in insert_job.batches:
                results += batch.get_results()
            insert_job.close_job()
            return results

        except Exception, e:
            print "Insert Failure: {}".format(e)

    def update(self, object, rows, chunksize=10000):
        try:
            update_job = BulkSalesforceJob(self, "update", object, chunksize=chunksize)
            total_rows = len(rows)
            print "Creating {}/{}={} chunks".format(total_rows, chunksize, total_rows / chunksize)
        except Exception, e:
            raise Exception("Unable to Create Salesforce Job: {}".format(e))
        
        try:
            for i in range(0, total_rows, chunksize):
                update_job.create_batch(rows[i:i + chunksize])
        except Exception, e:
            raise Exception("Unable to Create Salesforce Batch: {}".format(e))

        try:
            # Wait for the last batch to finish
            status = update_job.batches[-1].get_status()
            while (status["state"] != "Completed"):
                print "Update Status: {}".format(status["state"])
                status = update_job.batches[-1].get_status()
                time.sleep(1)
            results = []
            for batch in update_job.batches:
                results += batch.get_results()
            update_job.close_job()
            return results

        except Exception, e:
            print "Insert Failure: {}".format(e)

    def upsert(self, object, rows, externalId, chunksize=10000):
        try:
            upsert_job = BulkSalesforceJob(self, "upsert", object, externalId=externalId, chunksize=chunksize)
            total_rows = len(rows)
            print "Creating {}/{}={} chunks".format(total_rows, chunksize, total_rows / chunksize)
        except Exception, e:
            raise Exception("Unable to Create Salesforce Job: {}".format(e))
        
        try:
            for i in range(0, total_rows, chunksize):
                upsert_job.create_batch(rows[i:i + chunksize])
        except Exception, e:
            raise Exception("Unable to Create Salesforce Batch: {}".format(e))

        try:
            # Wait for the last batch to finish
            status = upsert_job.batches[-1].get_status()
            while (status["state"] != "Completed"):
                print "Upsert Status: {}".format(status["state"])
                status = upsert_job.batches[-1].get_status()
                time.sleep(1)
            results = []
            for batch in upsert_job.batches:
                results += batch.get_results()
            upsert_job.close_job()
            return results

        except Exception, e:
            print "Insert Failure: {}".format(e)






class BulkSalesforceJob(BulkSalesforce):
    def __init__(self, bulksalesforce, operation, object, externalId=None, chunksize=0):
        self.chunksize = chunksize
        self.operation = operation
        self.object = object
        self.externalId = externalId
        self.jobId = None # Will be populated after a job is created.
        self.batches = [] # Will be a list of BulkSalesforceBatch Objects
        self.bsf = bulksalesforce # Grab access to all the initiating class' instance variables
        self.create_job(self.operation, self.object, self.externalId) # Establish a Salesforce Bulk Job

    # Abstract request to Salesforce Bulk Job API
    def job_request(self, request):
        jobPath = "/" + self.jobId if self.jobId else ""
        url = "https://{}-api.salesforce.com/services/async/{}/job{}".format(
            self.bsf.instance, 
            self.bsf.version,
            jobPath
        )
        print "requesting {}: {}".format(url, json.dumps(request, indent=4))
        headers = { "X-SFDC-Session": self.bsf.sessionId, "Content-Type": "application/json" }
        if(self.chunksize > 0 and False): # This won't work until SFDC fixes: https://success.salesforce.com/issues_view?id=a1p300000008ZL6AAM
            headers.update({"Sforce-Enable-PKChunking": "chunkSize=" + str(self.chunksize)})
        return json.loads(
            requests.post(
                url = url,
                headers = headers,
                data = json.dumps(request),
                verify= False
            ).text
        )

    def create_job(self, operation, object, externalId=None):
        request = {
            "operation" : operation,
            "object" : object,
            "contentType" : "JSON"
        }
        if externalId is not None: 
            request.update({"externalIdFieldName" : externalId})
        # Fire the create job request                   
        response = self.job_request(request)
        if response.get('exceptionCode') is not None: # If there is an exception code, then the job failed
            raise Exception(response['exceptionMessage'])
        else: #otherwise we're good, assign the jobid as an instance variable
            self.jobId = response['id']


    def close_job(self):
        response = self.job_request({
            "state" : "Closed"
        })
        print json.dumps(response, indent=4)

    def create_batch(self, payload):
        self.batches.append(BulkSalesforceBatch(self, payload))
        print json.dumps(self.batches[-1].get_status(), indent=4)



class BulkSalesforceBatch(BulkSalesforceJob):
    def __init__(self, bulksalesforcejob, rows ):
        self.bsfj = bulksalesforcejob
        self.create_batch(rows)

    # Either performs a json.dumps or does not depending on if it's necessary
    def format_request(self, request):
        if (isinstance(request, basestring) or isinstance(request, str)):
            return request
        else:
            return json.dumps(request)

    def batch_create_request(self, request):
        headers = { "X-SFDC-Session": self.bsfj.bsf.sessionId, "Content-Type": "application/json" }
        url = "https://{}-api.salesforce.com/services/async/{}/job/{}/batch".format(
            self.bsfj.bsf.instance, 
            self.bsfj.bsf.version,
            self.bsfj.jobId
        )
        print "requesting {}: {}".format(url, json.dumps(request, indent=4))
        print "REQUEST TYPE: {}".format(isinstance(request, basestring))
        print "DATA: {}".format(request if type(request) is str else json.dumps(request))
        return json.loads(
            requests.post(
                url = url,
                headers = headers,
                data = self.format_request(request),
                verify= False
            ).text
        )

    def batch_status_request(self, result=False, resultId=None):
        result = "/{}".format('result') if result else ""
        resultId = "/{}".format(resultId) if (result and resultId is not None) else ""
        headers = { "X-SFDC-Session": self.bsfj.bsf.sessionId, "Content-Type": "application/json" }
        url = "https://{}-api.salesforce.com/services/async/{}/job/{}/batch/{}{}{}".format(
            self.bsfj.bsf.instance, 
            self.bsfj.bsf.version,
            self.bsfj.jobId,
            self.batchId,
            result,
            resultId
        )
        print "requesting status {}".format(url)
        return json.loads(
            requests.get(
                url = url,
                headers = headers,
                verify= False
            ).text
        )


    def create_batch(self, payload):
        response = self.batch_create_request(payload)
        if response.get('exceptionCode') is not None: # If there is an exception code, then the batch failed
            raise Exception(response['exceptionMessage'])
        else: #otherwise we're good, assign the batchid as an instance variable
            self.batchId = response['id']

    def get_status(self):
        return self.batch_status_request(result=False)

    # For inserts and updates
    def get_results(self):
        return self.batch_status_request(result=True)
    # For Queries
    def get_query_results(self):
        resultId = self.batch_status_request(result=True)[0]
        logger.info('Query Results Id. {}'.format(resultId))
        return self.batch_status_request(result=True,resultId=resultId)



















