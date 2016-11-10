## Mysql-poll

### Overview

The purpose of this Microservice is to retrieve all the rows in a specified query, and send them into Saasli. Currently, there exists only one method `poll` which leverages the bulk events api only. This means the use case is limited to `User_Usage_Event__c` records only. Plans to extend the method to a more all encompassing utility that can take any number of MySQL rows and create any different kind of SF Records id underway.

### Example

The following payload is expected by the microservice.

```json
{
     "client_id" : "saasli",
     "version" : "dev",
     "event_values" : {
          "Views__c" : "pageviews"
     },
     "event_name" : "Question Views",
     "event_id" : 1234,
     "mysql_id_column" : "id",
     "sf_object_id" : "Client_Product_Id__c",
     "sf_field_id" : "Breeze_Client_Id__c",
     "sf_lookup_id" : "Client_Product_Id__c",
     "query" : "SELECT * FROM users LIMIT 10"
}
```

| Parameter | Description | Inclusion |
| --------- | ----------- | -------- |
| client_id | The id of the client in the `clients` table in DynamoDB | &#x1F534;`required` |
| version | The Version of the mysql poll that is to be used. Cooresponds to the `stage` of the function | &#x1F534;`required` |
| event_name | The actual name of the event that has happened. A new UUHET record will be created if one doesn't already exist. | &#x1F534;`required` |
| mysql_id_column | "The column name in the MySQL query that holds the identifying triggering record value (the `sf_field_value` to the later defined `sf_field_id`)  | &#x1F534;`required` |
| sf_object_id | The SFDC Object of the record that triggered the event, and will be be associated to it. | &#x1F534;`required` | sf_field_id | The SFDC Field API name of the field that will be used to identify the triggering record. The value of which exists in the column specified by `mysql_id_column` | &#x1F534;`required` |
| sf_lookup_id | The SFDC API field name of the field on the Event record that will lookup the triggering sf object. It is typically named the same as the `sf_object_id`, however this offers the ability to use a different lookup field if one is so defined. | &#x1F534;`required` |
| query | A Valid SQL query that must return an id column as defined by `mysql_id_column` and any columns defined as values in the `event_values` object | &#x1F534;`required` |
| event_values | An SFDC Field API Name to MySQL Column mapping of additional values that shall be created with each event record. NOTE: That field must be created in SFDC, and that column name must exist in the MySQL query results | `optional` |
| event_id | The `events` endpoint has an optional paramter to override the default `Saasli_Event_Id__c` that is generated. This allows you to pass through that override in the form of the name of the column in the mysql row that houses the desired id. | `optional` |
