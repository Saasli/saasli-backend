**NOTE:** This requires a custom built version of psycopg2 to be able to run in lambda. It can be found [here](https://github.com/jkehler/awslambda-psycopg2)

## postgresql-poll

### Overview

The purpose of this Microservice is to retrieve all the rows in a specified query, and send them into Saasli from a postgresql database. Currently, there exists only one method `poll` which leverages the `objects` endpoint. The poller should be passed the object that the data rows are to be created as.

### Example

The following payload is expected by the microservice.

```json
{
     "client_id" : "saasli",
     "version" : "dev",
     "object" : "Inbound_API_Appointment__c",
     "external_id_field" : "External_Id_Field__c",
     "query" : "SELECT * FROM appointments LIMIT 10",
     "field_map" : {
        "name" : "Name",
        "id" : "External_Id_Field__c",
        "email" : "Customer_Email__c"
     }
}
```

| Parameter | Description | Inclusion |
| --------- | ----------- | -------- |
| client_id | The id of the client in the `clients` table in DynamoDB | &#x1F534;`required` |
| version | The Version of the postgres poll that is to be used. Cooresponds to the `stage` of the function | &#x1F534;`required` |
| object | The object that the data rows polled from postgres are to be created as in Salesforce. | &#x1F534;`required` | 
| external_id_field | The field on *object* that holds the external Id for the object. It must also have a cooresponding {field : value} pair in body for each record AND be of Data Type `(External ID)(Unique)` within Salesforce. | &#x1F534;`required` |
| query | A Valid SQL query | &#x1F534;`required` |
| field_map | A key:value mapping of the postgreSQL column name to the desired Salesforce Object field. Note: They must be of the same data type | &#x1F534;`required`  |

**NOTE:** as currently defined, posgres numeric values with decimals will be converted to strings.
