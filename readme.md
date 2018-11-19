
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

 Run `FLASK_APP=app.py` then `flask run` to execute `app.py`, which will be available at a localhost IP address.

on Windows: `$env:FLASK_APP='app.py'` `flask run`

Will be using html bootstrap for all [forms](https://getbootstrap.com/docs/4.0/components/forms/) and [buttons](https://getbootstrap.com/docs/4.0/components/buttons/)

For forms, likely going to use [WTForms](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms)

#### Zappa

Creates serverless web app architecture.

Deploy Zappa using [tutorial](https://www.viget.com/articles/building-a-simple-api-with-amazon-lambda-and-zappa/)

Called the project 'dev'. Deploy with: `zappa deploy dev`. Currently about 40MB. Porbably need to trim down unused packages.

To upload new code: `zappa update dev`


#### AWS Lambda

Code (flask app) is hosted on AWS, but is only invoked when triggered by user/visitor.

When deploying/updating to AWS with zappa on a new computer `zappa update dev`, you need to first configure AWS CLI again.

##### AWS Costing

With initial test, AWS lamda was being called regularly and free usage nearly expired.

used `zappa undeploy dev` to unstage the project before working out a fix

Perhaps related to the keep warm functin? `Unscheduled pathdojo-dev-zappa-keep-warm-handler.keep_warm_callback.`

Or otherwise might be related to the Quickstart.py file calling the api too often

#### DNS

Domain redirection set up as per [guid](https://github.com/Miserlou/Zappa/blob/master/docs/domain_with_free_ssl_dns.md)


#### Google Drive

Hosting images with each disease in separate folder.

API calls to be made by PyDrive for simplicity.

TODO: Allow the lambda instance API access, as per [stackoverflow comment](https://stackoverflow.com/questions/42170504/how-to-oauth-google-api-from-lambda-aws) and [google documentation](https://developers.google.com/identity/protocols/OAuth2ServiceAccount)

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

## Layout

Image [layout](https://www.samalive.co/) ideally scales with mobile browser


## Adding content

When creating a new disease, observe the following categories:

###### Organ
skin, lung, brain

###### Type
benign
malignant

###### Subtype
tumour
inflammatory
degenerative
vascular
infection
cystic

###### Complexity
 as a guide, the librpathology.org/spot_diagnosis and /short_power_list and /long_power_list are used to determine complexity category
spot_diagnosis
basic
advanced (long power list minus (short power list and spotters)
curiosity (really niche things)

###### Incidence
common
uncommon
rare

###### Name
disease name with underline delimiters in the format: this_is_a_disease_name

