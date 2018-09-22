# Goal: Use pathdojo on any device through the browser

Structure:
python code / app logic: Hosted on cloud server (e.g. AWS)

zappa.io packages code so that it can be hosted on AWS lambda

when the user sends a request, it spins up an instance on AWS lambda which executes the code then closes down

code will retrieve file from google drive using the google drive API

Flask is used to glue everything together, runs app logic, communicates with frontend. Flask is what will be deployed with Zappa.



# TODO

Flaskify python code

Deploy Zappa https://www.viget.com/articles/building-a-simple-api-with-amazon-lambda-and-zappa/

Called the project 'dev'
usage: zappa deploy dev
upload new code: zappa update dev 


