import sys
from tools import *
sys.path.insert(0, './mysql-poll-venv/lib/python2.7/site-packages/') #TODO: Keep an eye out for serverless recognizing venvs and packaging them automatically
import logging, json, pymysql.cursors, requests, time
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def poll(event, context):
    # Get a class instance of lambda microservice
    try:
        functions = Microservice(event['version']) # get a class level microservice client
    except:
        raise Exception({"error" , "couldn't instantiate functions"})

    # Get the SFDC credentials
    try:
        databaseCredentials = DatabaseCredentials(event['client_id'], functions)
    except:
        raise Exception("error" , "couldn't get db creds")


    #Connect to the database
    connection = pymysql.connect(
        host=databaseCredentials.host,
        user=databaseCredentials.user,
        password=databaseCredentials.password,
        db=databaseCredentials.db,
        charset=databaseCredentials.charset,
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        logger.info("Opening MySQL Cursor.")
        with connection.cursor() as cursor:
            cursor.execute(event['query'])
            rows = cursor.fetchall()
            events = [] #instantiate the events array
            for row in rows: #build the events array
                ev = {}
                for key, value in event['event_values'].items(): #Build the required event values
                    ev.update({ key : row[value] })
                events.append({
                    "sf_field_value" : row['id'],
                        "event" : {
                            "event_name" : event['event_name'],
                            "event_timestamp" : int(time.time()),
                            "event_values" : ev
                        }
                })

            insert_payload = {
                "path" : {}, #required to pass the Request
                "body" : {
                    "client_id" : event['client_id'],
                    "sf_object_id" : event['sf_object_id'],
                    "sf_field_id" : event['sf_field_id'],
                    "sf_lookup_id" : event['sf_lookup_id'],
                    "events" : events
                }
            }
            functions.request('api', 'events', insert_payload)


    finally: #Kill the connection even if an exception is thrown
        logger.info("Tear Down MySQL Connection.")
        connection.close()

    return 1