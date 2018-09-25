# Goal: Use pathdojo on any device through the browser

Structure:
python code / app logic: Hosted on cloud server (e.g. AWS)

zappa.io packages code so that it can be hosted on AWS lambda

when the user sends a request, it spins up an instance on AWS lambda which executes the code then closes down

code will retrieve file from google drive using the google drive API

Flask is used to glue everything together, runs app logic, communicates with frontend. Flask is what will be deployed with Zappa.


# Flask component

Turns python code into a web app.

## Testing

`MY_FLASK_APP=app.py flask run` Will run app.py 

## TODO

Flaskify the quiz

# Zappa

Creates serverless web app architecture.

Deploy Zappa tutorial: https://www.viget.com/articles/building-a-simple-api-with-amazon-lambda-and-zappa/

Called the project 'dev'

Usage: `zappa deploy dev` 

Currently about 40MB. Porbably need to trim down unused packages.

Upload new code: `zappa update dev`


# AWS Lambda

Code (flask app) is hosted on AWS, but is only invoked when triggered by user/visitor.

# Google Drive

Hosting images with each disease in separate folder.

API calls to be made by PyDrive for simplicity.

# TODO

Replace local file calls in quiz code with API calls to drive.





