import sys
from tools import *
sys.path.insert(0, './venv/lib/python2.7/site-packages/') #TODO: Keep an eye out for serverless recognizing venvs and packaging them automatically
import json, psycopg2, logging, decimal, datetime, time, re
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Check if value is a datetime.datetime
def ismysqldatetime(val):
    try:
        return isinstance(val, datetime.date)
    except: #Catch any other format
        return False

def isdecimal(val):
    try:
        return isinstance(val, decimal.Decimal)
    except:
        return False

# Take a datetime, return a unix timestamp int
def datetime2unix(date):
    return int(time.mktime(date.timetuple()))

def decimal2string(decimal):
    return str(decimal)


def poll(event, context):
    # -----------------------------------------------------------------------
    # 1) Collect all the parameters and verify that they are in fact provided
    # -----------------------------------------------------------------------

    # Get the SFDC Object name
    try:
        salesforceObject = event['object']
        fieldMap = event['field_map']
        externalIdField = event['external_id_field']
        query = event['query']
        clientId = event['client_id']
        version = event['version']
    except:
        raise KeyError("error" , "No '{}' provided.".format(e))

    # -----------------------------------------------------------------------
    # 2) Establish microservice connection utility and retrieve database credentials
    # -----------------------------------------------------------------------

    # Get a class instance of lambda microservice
    try:
        functions = Microservice(version) # get a class level microservice client
    except Exception, e:
        raise Exception({"error" , "couldn't instantiate functions {}".format(e)})

    # Get the database credentials
    try:
        databaseCredentials = DatabaseCredentials(clientId, functions)
    except:
        raise Exception("error" , "Could not retrieve db credentials, is 'client_id' : {} valid?".format(event['client_id']))


    # ------------------------------------------------------------------------------------------
    # 3) Establish a connection to the postgreSQL database, open a cursor, perform the query and 
    #    close the cursor and DB connection.
    # ------------------------------------------------------------------------------------------

    # Connect to the DB
    try:
        connection = psycopg2.connect(
            dbname=databaseCredentials.dbname,
            database = databaseCredentials.database,
            user = databaseCredentials.user,
            password = databaseCredentials.password,
            host = databaseCredentials.host,
            port = databaseCredentials.port
        )
    except Exception, e:
        raise Exception("Unable to connect to {}: {}".format(databaseCredentials.dbname, e))
        
    # Open up the cursor
    try:
        cursor = connection.cursor()
    except Exception, e:
        raise Exception("Error establishing cursor: {}".format(e))

    # Fire the query and collect the results
    try:
        # Add last_id to query to collect new rows.
        logger.info("last_id: {}".format(databaseCredentials.last_id))
        query = event['query']
        if salesforceObject == 'Inbound_API_Survey_Response__c':
            query = "{}{}".format(query, databaseCredentials.last_id)
        logger.info("query: {}".format(query))
        cursor.execute(query)
        columnNames = [desc[0] for desc in cursor.description] # get the names of the columns
        postgresRows = cursor.fetchall()
        if len(postgresRows) == 0: #we're done if there are no new rows
            return {"Result" : "No new Rows"}
        newLastId = postgresRows[-1][0]
        logger.info("Rows polled: {}".format(len(postgresRows)))
    except Exception, e :
        raise Exception("Error performing query {}: {}".format(query, e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    # ------------------------------------------------------------------------------------------
    # 4) Enumerate through the rows retrieved and create a record upload array
    # ------------------------------------------------------------------------------------------
    records = []
    for i, record in enumerate(postgresRows):
        result = {}
        for postgresName, salesforceName in fieldMap.items(): #iterate through the field map
            recordValue = record[columnNames.index(postgresName)] #get the postgreSQL column value
            if ismysqldatetime(recordValue): #if this representative of a date or datetime
                logger.info("pgname: {}".format(postgresName))
                logger.info("sfname: {}".format(salesforceName))
                logger.info("datetime: {}".format(recordValue))
                recordValue = recordValue.isoformat() #convert it to a isoformat stamp
            if isdecimal(recordValue): #check to see if the variable is of decimal type
                recordValue = decimal2string(recordValue) #convert to a string
            #if isDecimal(recordValue): #if this is representative of a decimal, make it a string. 
            result.update({ salesforceName : recordValue })
        records.append(result)

    # ------------------------------------------------------------------------------------------
    # 5) Build and send a payload of records to the /objects microservice for upload
    # ------------------------------------------------------------------------------------------
    logger.info("Records to be upserted: {}".format(len(records)))
    functions.request('api', 'objects', {
        "path" : {
            "client_id" : clientId,
            "object" : salesforceObject,
            "external_id" : externalIdField
        },
        "body" : {
            "records" : records
        }
    })
    # ------------------------------------------------------------------------------------------
    # 6) Update the database with the last queried id (only for survey responses)
    # ------------------------------------------------------------------------------------------
    if salesforceObject == 'Inbound_API_Survey_Response__c':
        databaseCredentials.update_id(newLastId)
    return {'success' : 'true'}
