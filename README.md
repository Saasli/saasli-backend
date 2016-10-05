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
pip freeze >> requirements.txt
```

### Contracts

All the functions in `utils` operate on a 'Contract' convention. They will always return a payload of the format:

For a Success:
```
{ 
	'error' : False,
	'response' : ... # where this is the documented response dict
}
```

For an Error:
```
{ 
	'error' : True,
	'message' : 'Desicription of what went wrong' 
}
```