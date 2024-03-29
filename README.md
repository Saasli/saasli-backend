# saasli-backend

## API Reference
See the [documentation](https://saasli.github.io/docs/).

##Getting Started

###Quick Install

1) Clone this repo
```
cd ~
git clone git@github.com:Saasli/saasli-backend.git
```

2) Get yourself the latest serverless from npm

```
npm install -g https://github.com/serverless/serverless
```

3) Get `virtualenv` to be able to deploy all the python requirements

```
pip install virtualenv
```

###Nomenclature 

- *service* : Each of the sub directories beneath `/api` and `utils` are separate serverless services. The difference is that we hook `/api` services up to the API gateway so the world can access them. `/utils` by contrast are only accessible by other lambda functions.
- *function* : Within each service are functions. For example beneath the `/account` service we have `accounts` and `account`.


##Developing a Service

### Naming Convention

Serverless names services with the following scheme {service_name}-{stage}-{function_name}. We strip the name of the stage out assuming this convention so it's imparative that service names, stage names and function names only contain alphanumeric characters. 

### Creating a Service

The serverless CLI makes this simple and quick. The first step is to create a new directory to house the service. There are two different flavours of services in this repo, `utils` and `api`. The `api` is actually one big service in itself, so adding new functionality to it isn't _technically_ creating a service rather a new function, but we'll cover that here.

#### Creating a new API function

1) Change into the `api` directory and create a new folder and files. The folder structure attempts to mirror how this will ultimately appear in the API Gateway.

```
cd ./api/
mkdir <FUNCTION_NAME>
vim ./handler.py
```
paste in the following:

```
from tools import *
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def <FUNCTION_NAME>(event, context):
	return {'Message' : 'Unimplemented'}
```

exit vim with `<ESCAPE> + :wq`


2) Ammend the `serverless.yml` to encompass the new function. Open up the `serverless.yml` in a text editor and add the following (FUNCTION_NAME must match the name of the folder as defined in step 1)) In the `functions` array append the following.

```
<FUNCTION_NAME>:
    timeout: 60
    handler: <FUNCTION_NAME>/handler.<FUNCTION_NAME>
    events:
      - http:
          integration: lambda
          method: post
          path: <FUNCTION_NAME>/
    package:
      include:
        - <FUNCTION_NAME>
```

*NOTE:* All the other functions within `api` have a `brokers.py` file to handle the processing of the json payload. It is reccomended that this convention be followed, however not compulsory.

#### Creating a new `utils` service

1) Navigate to the `utils` directory, and create a new directory with the desired service name.

```
cd ./utils
mkdir <SERVICE_NAME>
cd <SERVICE_NAME>
```

2) Use the serverless CLI to construct the new service

```
serverless create --template aws-python --name <SERVICE_NAME>
```

*NOTE* Other templates for Node.js and Java exist, however python is the preferred language of this repo.

### Virtual Environments

Serverless upon deployment will zip up everything it it's directory. Then, when live on Lambda it will only have access to anything in that zip. This is a problem if your code needs some python libraries because beyond a few pretty generic ones like `boto3`, none are included. To get around that, and have only files required for a given service be zipped, we use virtual environments. 


#### If you don't already have a venv
1) Globally install virtualenv if you don't already have it
```
pip install virtualenv 
```
2) Navigate to the service and establish a venv
``` 
cd <~/SERVICE/DIRECTORY/FILE/PATH>
virtualenv ./<SERVICE_NAME>_venv
```
3) Enter the venv
```
source <SERVICE_NAME>_venv/bin/activate
```
4) Get all the requirements (if a requirements.txt file exists)
```
pip install -r requirements.txt
```

#### If you already have a venv
1) `cd` in to the service directory and enter the venv
```
source <SERVICE_NAME>_venv/bin/activate
```
2) To get out of the venv run
```
deactivate
```

If you need to add some new python libraries make sure that you're in the correct virtual env for the given service and that you're running 
```
pip install |LIBRARY_NAME|
pip freeze > requirements.txt
```

### Contracts

All the functions in `utils` operate on a 'Contract' convention. They will always return a payload of the format. Whenever one is called, be sure to check for the existance of `errorType` as an exception thrown in one will return that.