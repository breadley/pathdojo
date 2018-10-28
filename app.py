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
            print('selected_files about to be processed for subfiles', selected_files)
            # Go through the selected files and take invetory of subfiles
            selected_files_and_subfiles = gdrive_api_calls.add_subfiles_to_file_details(selected_files, google_drive=google_drive)
            print('selected_files with subfiles', selected_files_and_subfiles)
            # Create quiz

            # fully_formed_quiz = quiz_logic.Quiz(selected_files,max_quiz_length,google_drive = google_drive)
            
            # fully_formed_quiz.step_through_quiz()
            
            ###########temporary random file test############
            random_disease = random.choice(selected_files_and_subfiles)
            random_disease_images = []
            for subfile in random_disease["files_within_folder"]:
                if subfile['subfile_type']=='image':
                    random_disease_images.append(subfile)

            random_image = random.choice(random_disease_images) 

            test_image_id = random_image['subfile_id']
            test_image_name = random_image['subfile_name']
            test_disease_name = random_disease['printable_name']

            # Save the image variables as a sessin for /view to access
            session['test_image_id'] = test_image_id
            session['test_image_name'] = test_image_name
            session['test_disease_name'] = test_disease_name


            return render_template('view.html', image_id = test_image_id,form_value = request.form)

    return render_template('design.html', 
                            message = message,
                            selections = selections,
                            available_category_options = available_category_options)




@app.route('/view',methods=['GET', 'POST'])
def view():
    # This page is for viewing the current disease in the quiz

    # TEMP TEST Get the details of the current image
    test_image_id = session.get('test_image_id', None)
    test_image_name = session.get('test_image_name',None)
    test_disease_name = session.get('test_disease_name',None)
    # If anything is posted, display the test image
    if request.method == 'POST':
        answer = f'The answer is: {test_disease_name}'
        return render_template('view.html', image_id = test_image_id, answer = answer)

    """ WORK IN PROGRESS. CURRENTLY BELIEVE QUIZ WILL BE EXECUTED FROM HERE. 
    # Caching (to be attempted later) will have happened in /design prior to coming to view

    # Create quiz object - > or do this in /design

    # Get the first element from the quiz

    # Render the image and buttons for IHC/ddx/clue/nestedquiz/answer_description/terminate/skip

    # If button pressed for options such as IHC, also display IHC

    # If button pressed for next image, render /view again with the new disease as the current disease

    # 

    """

    return render_template('view.html', image_id = test_image_id, form_value = request.form)



@app.route('/')
def index():
    # Homepage    
    message = 'Hi there'    
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
            # download the image
            downloaded_file_name = gdrive_api_calls.download_single_image(subfile['subfile_id'],subfile['subfile_name'])
            # Return the image name
            return downloaded_file_name


@app.route('/display',methods=['GET', 'POST'])
def display():

    message = string_to_html(dojo_welcome)

    # Get inventory from '/' home page or take manually if not already available.
    available_files = gdrive_api_calls.record_available_files(google_drive = True)
    
    successes = session.get('successes', 0)
    # Get a random disease
    
    # Check to see if there is a blob stored yet
    blob = session.get('blob', get_random_disease(available_files)[0])
    blob_name = blob[0]['printable_name']

    # Assign the disease to the session
    session['blob'] = blob
    print(f'This blob is {blob_name}')
    # blob = session.get('blob', get_random_disease(available_files))

    if request.method == 'POST':

        guess = request.form.get('blob')

        if guess.lower() == blob['printable_name'].lower():

            session['successes'] = successes + 1
            session['blob'] = get_random_disease(available_files)

            return redirect('/display')

        else:
            session['successes'] = 0
            # Randomise the blob for the next turn
            session['blob'] = get_random_disease(available_files)[0]

            return render_template('wrong.html', successes=successes, blob_name=blob_name)
    # Download image
    downloaded_file_name = get_random_image(blob)  
    
    return render_template('display.html', image_name=downloaded_file_name, message=message, successes=successes, failed=True, name=blob_name)


# include this for local dev
if __name__ == '__main__':
    app.run(debug=True)
 
    
