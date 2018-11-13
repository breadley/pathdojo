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

 
@app.route('/',methods=['GET','POST'])
def design():
    google_drive = True
    message = 'Select categories to include, or go straight into a random quiz'
 
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

    current_disease = session.get('current_disease',None)
    disease = quiz_logic.Disease(current_disease,google_drive=True)
    disease.take_subfile_inventory()

    # Need to replace this with in-memory IO (import IO)
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
        
                # Get next item in quiz (pop)
            if len(current_quiz['list_of_selected_files']) == 0:
                return redirect('/')
            
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
          
    positive_immunohistochemistry = ''
    negative_immunohistochemistry = ''
    for ihc in disease.immunohistochemistry:
        if disease.immunohistochemistry[ihc] == '+':
            positive_immunohistochemistry+=ihc+'   '
        if disease.immunohistochemistry[ihc] == '-':
            negative_immunohistochemistry+=ihc+'   '
    answer = disease.name
    differentials = disease.differentials
    session['differentials'] = differentials # Save in case DDx quiz initiated

    print(f'\tdescription: {disease.description}\n\nimmunohistochemistry: {disease.immunohistochemistry}\n\tdifferentials: {differentials}\n\tanswer: {answer}')

    # Pass the necessary values/dicts to the view page
    return render_template('view.html', 
                            description = disease.description,
                            immunohistochemistry = disease.immunohistochemistry,
                            positive_immunohistochemistry = positive_immunohistochemistry,
                            negative_immunohistochemistry = negative_immunohistochemistry,
                            differentials = differentials,
                            image_ids = image_ids,
                            answer = answer)



@app.route('/info')
def index():
    # Homepage    
    message = 'Reinforcement learning for familiarity with basic disease morphology'    
    return render_template('info.html',message = message)


@app.route('/differentials')
def differentials():
    # View differentials  
    differentials = session.get('differentials')
       
    return render_template('differentials.html',differentials = differentials)

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





# include this for local dev
if __name__ == '__main__':
    app.run(debug=True)
 
    
