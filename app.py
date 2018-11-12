from flask import Flask, render_template, redirect, request, session, url_for
import config
import os
import gdrive_api_calls
import random
import quiz_logic
import pdb
import json


app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')

# Debug mode on/True or off/False
app.debug=True

# Inventory needs to only be taken once
need_to_take_inventory = True

dojo_welcome = """ Hello there """



def take_inventory():
    # TO BE DEPRECATED
    # This function creates a dictionary of files with attributes 
    # IDs are from google drive

    # [{'name':'blah','google_drive_id':'id','folder_name':'blah'}]

    # Get list from API using function that uses PyDrive
    for folder_name,google_drive_id in gdrive_api_calls.list_all_files('dummy_folder').items():
        # Create disease attributes
        this_disease={}
        this_disease['folder_name'] = folder_name
        this_disease['google_drive_id'] = google_drive_id
        this_disease['underlined_name'] = folder_name.split('][')[5].strip(']')
        # replace underlines with spaces
        this_disease['name'] = ''
        for letter in this_disease['underlined_name']:
            if letter == '_':
                this_disease['name']+=' '
            else:
                this_disease['name']+=letter

        # Add to globally addressable list
        list_of_files_with_attributes.append(this_disease)

def string_to_html(string):
    modified_string = string\
            .replace(" ","&nbsp;")\
            .replace(">","&gt;")\
            .replace("<","&lt;")\
            .replace("\n","<br>")
    return modified_string

 
@app.route('/design',methods=['GET','POST'])
def design():
    # WORK IN PROGRESS - CANNOT GET INPUTS FROM MORE THAN ONE BUTTON AT A TIME
    google_drive = True
    # Homepage 
    message = 'Buttons, buttons, everywhere. \nWhich things will you choose?'
 
    # Get inventory (ideally we would only do this the first time)
    
    available_files = gdrive_api_calls.record_available_files(google_drive = google_drive)


    available_category_options = quiz_logic.get_category_options(available_files)

    selected_category_options = {}
    for category in available_category_options.keys():
        selected_category_options[category]=[]

    temp_selections = []

    # Create a blank dictionary to hold button presses
    selections = session.get('selections', temp_selections)
    
    
    # If a button is pressed
    if request.method == 'POST':
        selections = request.form.to_dict()
        print(selections)
        JSONmemory = selections['memory']
        memory = json.loads(JSONmemory)
        selected_category_options = memory['category_selections']
        max_quiz_length = memory['quiz_length']        

        # If the submit button is pressed
        if selections['submit_button'] == 'pressed': 
            



            selected_files = quiz_logic.get_filenames_that_match(available_files,selected_category_options)
            
            # Remove the last element, and assign as the current disease
            session['current_disease'] = selected_files.pop()                  
            
            # Record this quiz in the master list
            this_quiz = {}
            this_quiz['unique_id'] = random.getrandbits(32)
            this_quiz['thumbnail'] =  None
            this_quiz['list_of_selected_files'] = selected_files

            # Set initial values for each of the global variables

            # A list of dictionaries with: quiz_id, quiz_selected_files, thumbnail
            session['list_of_quizzes'] = [this_quiz]
            
            # A list of disease dictionaries with: name, drive id, ... but not folder contents
            session['current_quiz'] = this_quiz
          
            return view()

    return render_template('design.html', 
                            message = message,
                            selections = selections,
                            available_category_options = available_category_options)




@app.route('/view',methods=['GET', 'POST'])
def view():
    # This page is for viewing the current disease in the quiz

    differentials = ''
    immunohistochemistry = ''
    description = ''

    current_quiz = session.get('current_quiz',None)

    # Get next item in quiz (pop)
    if len(current_quiz) == 1:
        pass
        # finished the quiz, do things here 

    current_disease = session.get('current_disease',None)
    disease = quiz_logic.Disease(current_disease,google_drive=True)
    disease.take_subfile_inventory()
    disease.download_non_image_files()
    images = disease.images
    image_ids = []
    for image in disease.images:
        image_ids.append(image['subfile_id'])


    if request.method == 'POST':
        print('request.form is: ',request.form)
        if request.form.get('guess') == disease.name:
            print('hot dog, we have a winner!')

        if request.form.get('move_on') == 'Next': # if the move on button has been primed
            print('moving to next item')
            
            # Get the old list, remove the last element and assign as current disease
            print('before',len(current_quiz['list_of_selected_files']))
            session['current_disease'] = current_quiz['list_of_selected_files'].pop()
            print('after',len(current_quiz['list_of_selected_files']))
            # update current quiz
            session['current_quiz'] = current_quiz



        if request.form.get('skip_option') == 'skipping':
            # Remove the last element from the quiz, and assigne it as the current disease
            session['current_disease'] = current_quiz.pop()
            print('we are skipping this disease')

        return redirect('/view')
        


    answer = disease.name

    print(f'\tdescription: {description}\n\nimmunohistochemistry: {immunohistochemistry}\n\tdifferentials: {differentials}\n\tanswer: {answer}')

    # Pass the necessary values/dicts to the view page
    return render_template('view.html', 
                            description = disease.description,
                            immunohistochemistry = disease.immunohistochemistry,
                            differentials = disease.differentials,
                            image_ids = image_ids,
                            answer = answer)



@app.route('/')
def index():
    # Homepage    
    message = 'Hi there'    
    session['unique_public_session_id'] = random.getrandbits(32)
    cookie = session.get('unique_public_session_id','no cookie')
    print('Cookie is',cookie)
    return render_template('index.html',message = message)


def get_single_image(blob_folder_drive_id):
    # This function randomly chooses an image from a blob's folder and downloads it for display

    # first clear the static folder (a cache for image to be displayed)
    for old_image in os.listdir('static'):
        os.remove('static/'+old_image)

    # Get image id's
    blob_folder_image_ids = gdrive_api_calls.get_file_ids_from_folder(blob_folder_drive_id)[0] # 1 is for text, 0 for images
    # Download a single image
    random_image_filename = gdrive_api_calls.select_an_image_from_list_of_ids(blob_folder_image_ids)[0]
    random_image_id = gdrive_api_calls.select_an_image_from_list_of_ids(blob_folder_image_ids)[1]
    
    # Return image name
    return random_image_filename


def get_random_disease(available_files=[]):
    # This function returns a single disease dictionary for simple displaying

    disease = []
    # Pick a random disease
    disease.append(random.choice(available_files))
    # Get the folder details
    detailed_disease = gdrive_api_calls.add_subfiles_to_file_details(disease, google_drive=True)
    return detailed_disease

def get_random_image(detailed_disease_dictionary):
    # This function picks a random image ID to display


    files = detailed_disease_dictionary['files_within_folder']

    for subfile in files:
        if subfile['subfile_type'] == 'image':
            # download the image using the subfile dictionary
            gdrive_api_calls.download_subfile(subfile)
            # Return the image name
            
            return subfile['temporary_file_name']


@app.route('/display',methods=['GET', 'POST'])
def display():

    message = string_to_html(dojo_welcome)

    # Get inventory from '/' home page or take manually if not already available.
    # Don't get inventory if POST form (to avoid unnecessary API call)
    print(f'\n\nrequest variable is: {request.form}\n\n')
    available_files = gdrive_api_calls.record_available_files(google_drive = True)
    
    successes = session.get('successes', 0)
    # Get a random disease
    
    # Check to see if there is a blob stored yet
    blob = session.get('blob', get_random_disease(available_files)[0])
    print("The blobby is",blob)
    blob_name = blob['printable_name']
    # Assign the disease to the session
    session['blob'] = blob
    print(f'This blob is {blob_name}')
    # blob = session.get('blob', get_random_disease(available_files))
    
    
    # Test OOP functionality    
    blob_object = quiz_logic.Disease(blob,google_drive=True)
    print("blobject is", blob_object)


    if request.method == 'POST':

        guess = request.form.get('blob')

        if guess.lower() == blob['printable_name'].lower():

            session['successes'] = successes + 1
            session['blob'] = get_random_disease(available_files)[0]


            return redirect('/display')

        else:
            session['successes'] = 0
            # Randomise the blob for the next turn
            session['blob'] = get_random_disease(available_files)[0]

            # Clear static folder
            for file in os.listdir(config.google_drive_download_directory):
                os.remove(config.google_drive_download_directory+file)

            return render_template('wrong.html', 
                                    successes=successes, 
                                    blob_name=blob_name, 
                                    ihc=blob_object.immunohistochemistry,
                                    ddx=blob_object.differentials,
                                    description=blob_object.description)
    # Download image
    downloaded_image_name = get_random_image(blob)
    
    print('image name', downloaded_image_name)
    print('download folder contents',os.listdir(config.google_drive_download_directory))
    
    while downloaded_image_name not in os.listdir(config.google_drive_download_directory):
        print('waiting')
       
    
    
    return render_template('display.html', image_name=downloaded_image_name, 
                            message=message, 
                            successes=successes, 
                            failed=True, 
                            name=blob_name,
                            images=blob_object.images)


# include this for local dev
if __name__ == '__main__':
    app.run(debug=True)
 
    
