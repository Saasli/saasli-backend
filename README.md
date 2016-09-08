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

- *service* : Each of the sub directories beneath `/api` and `utils` are separate serverless services. The difference is that we hook `/api` services up to the API gateway so the world can access them. 
- *function* : Within each service are functions. For example beneath the `/account` service we have `accounts` and `account`.


###Developing a Service

Serverless upon deployment will zip up everything it it's directory. Then, when live on Lambda it will only have access to anything in that zip. This is a problem if your code needs some python libraries because beyond a few pretty generic ones like `boto3`, none are included. To get around that, and have only files required for a given service be zipped we use virtual environments. 

Whenever you want to work on a service `cd` in to the directory and run
```
source |SERVICE_NAME|_venv/bin/activate
```
To get out of the venv run
```
deactivate
```

If you need to add some new python libraries make sure that you're in the correct virtual env for the given service and that you're running 
```
pip install |LIBRARY_NAME|
pip freeze > requirements.txt
```