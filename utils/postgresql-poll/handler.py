import sys
#sys.path.insert(0, './venv/lib/python2.7/site-packages/') #TODO: Keep an eye out for serverless recognizing venvs and packaging them automatically
import json, psycopg2

def poll(event, context):
    try:
        print "connecting?"
        connection = psycopg2.connect(
            dbname="test_postgres",
            database = "test-postgres",
            user = "hgoddard",
            password = "salesforce1",
            host = "test-postgres.czqasnwpdim9.us-east-1.rds.amazonaws.com",
            port = 5432
        )
        print connection

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        print cursor.fetchall()
    except Exception, e:
        print "whoops!: {}".format(e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }

poll(None, None)