
## Motivation

Histology is pattern recognition with reinforcement. This is a tool to create bite-sized custom image quizzes. 

###### Strategy

Curate a library of notes and images and view them with a website dynamically.

###### Additional functions: 
- Read simple disease refreshers
- Inspect immunohistochemistry and differentials
- Generate a differentials quiz-within-a-quiz for comparing like-diseases instantly

## Goal: Study histology on any device through the browser

### Structure:

- Python code / app logic: Hosted on cloud server (e.g. AWS)

- Zappa.io packages code so that it can be hosted on AWS lambda

- When the user sends a request, it spins up an instance on AWS lambda which executes the code then closes down

- Code will retrieve file from google drive using the google drive API

- Flask is used to glue everything together, runs app logic, communicates with frontend. Flask is what will be deployed with Zappa.


#### Flask component

Turns python code into a web app using [litera](https://bootswatch.com/litera/) formatting

###### Testing

`FLASK_APP=app.py` `flask run` Will run `app.py`

on Windows: `$env:FLASK_APP='app.py'` `flask run`


#### Zappa

Creates serverless web app architecture.

Deploy Zappa using [tutorial](https://www.viget.com/articles/building-a-simple-api-with-amazon-lambda-and-zappa/)

Called the project 'dev'. Deploy with: `zappa deploy dev`. Currently about 40MB. Porbably need to trim down unused packages.

To upload new code: `zappa update dev`


#### AWS Lambda

Code (flask app) is hosted on AWS, but is only invoked when triggered by user/visitor.

When deploying/updating to AWS with zappa on a new computer `zappa update dev`, you need to first configure AWS CLI again.

#### Google Drive

Hosting images with each disease in separate folder.

API calls to be made by PyDrive for simplicity.

## Structure and relationship of components

##### app.py

0. If first time running, clears /cache folder, gets file inventory and passes to design.html for the user to input selections

2. Reqeives `POST`ed list of selections, passes parameters to `quiz.py` to get quiz objects

4. Records quiz object in dictionary of quizzes and caches all files required for the quiz

5. Checks what the current quiz is and, sends the current disease of that quiz to `display.html`

7. If `POST` message received, take appropriate action:

    - display_differentials: send list of differentials to `display.html`

    - get_clue: send clue text to `display.html`

    - start_a_nested_quiz: 

    - show_name_and_description: return list to `display.html`

    - terminate_quiz: clears cache of current quiz and then removes quiz from quiz dictionary

    - skip_answer: get next disease with `disease.step_through_quiz()`


##### *.html 

1. `design.html` accepts inventory, displays options, gets user inputs, `POST`s list to app.py 

6. Receives a disease object, displays images, asks user for answer/options, `POST`s answer/options to app.py

##### quiz.py 

3. Accpts selections, creates quiz object, sends list to `app.py`

##### api_calls.py 

May be used for google drive calls, may be incoroporated into `app.py`




