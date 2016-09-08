#!/bin/bash
cp -R ../utils . #make a copy of the global utils directory at the service level
source ./account_venv/bin/activate #enter the venv
pip install -r ./requirements.txt -t ./lib #get all the uninstalled python libs in the /lib folder
sls deploy #send this puppy up to AWS
rm -rf ./utils #hide the body
