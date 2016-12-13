### Objects Endpoint

#### URL Params (path)

```
/{client_id}/bulk/{object}/{external_id}
```

| variable | purpose | example |
| -------- | ------- | ------- |
| *client_id* | The Salesforce environment to be upserted to. Credentials must be stored in DynamoDB with cooresponding Id as the key | 0911C95B-74E0-4607-A855-2C91973B93B0 |
| *object* | The Salesforce object that records in the body are representing | Event__c |
| *external_id* | The field on *object* that holds the external Id for the object. It must also have a cooresponding {field : value} pair in body for each record AND be of Data Type `(External ID)(Unique)` | Unique_Field__c |

#### Body (body)

e.g.
```
{
    "records" : [
        {
        	"Dispatch_Appointment_Id__c" : 7,
            "Account__c" : {
                "object" : "Account", #The Object Type this lookup relates to
                "field" : "Website", #The field on the looked up object that identifies it
                "unique_value": "www.acme2.com" #The unique value in field `field` that identfies the lookup
            }
        },
        {
            "Dispatch_Appointment_Id__c" : 23,
            "Account__c" : {
                "object" : "Account",
                "field" : "Name",
                "unique_value": "ACME X"
            }
        }
    ]
}
```

| variable | data type | purpose |
| -------- | --------- | ------- |
| *records* | array | Represents all records to be upserted. *NOTE:* One field must coorespond to the `unique_id` specified in the url. All fields must be of type `integer` or `string` UNLESS they are a lookup field in which case the structure must be as shown in the example. |

