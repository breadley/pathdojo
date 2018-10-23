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


# [{'name':'blah blah','underlined_name':'blah_blah','google_drive_id':'id','folder_name':'blah'}]
list_of_files_with_attributes = []
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
    # We will use local files for the moment
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
            # Go through the selected files and take invetory of subfiles
            selected_files_and_subfiles = gdrive_api_calls.add_subfiles_to_file_details(selected_files, google_drive=True)
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
    

    if request.method == 'POST':
        answer = f'The answer is: {test_disease_name}'
        return render_template('view.html', image_id = test_image_id, answer = answer)
            
    return render_template('view.html', image_id = test_image_id, form_value = request.form)



@app.route('/')
def index():
    # Homepage    
    message = 'Hi there'
    return render_template('index.html',message = message)


@app.route('/files/')
def files():
    # Deprecated/gdrive test only
    # Homepage/files
    content = ''

    # TODO, replace code here with a call to take_inventory
    # assign all the files to the global variable dictionary_of_files
    temp_files = gdrive_api_calls.list_all_files('dummy_folder')
    for filename,id in temp_files.items():
        # if file is a disease folder
        if filename.startswith('[') and filname.endswith(']'):
            # add file to globally acccessible list
            dictionary_of_files[filename] = id
            content+=f'\n\nFilename: {filename}\t\t\tFile ID: {id}'
    

    page = string_to_html_page(content)

    # use a monospace font so everything lines up as expected
    return page, 200   

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


@app.route('/display',methods=['GET', 'POST'])
def display():
    # Intro message TODO
    message = string_to_html(dojo_welcome)

    # Take inventory of files (ideally once only)
    '''
    if need_to_take_inventory:
        take_inventory()
        need_to_take_inventory=False
    '''
    take_inventory()

    # Reference the diseases as blobs for testing
    blobs = list_of_files_with_attributes

    successes = session.get('successes', 0)
    # Get a random disease
    blob = session.get('blob', random.choice(blobs))
    # Assign the disease a to the session
    session['blob'] = blob


    if request.method == 'POST':

        guess = request.form.get('blob')

        if guess.lower() == blob['name'].lower():

            session['successes'] = successes + 1
            session['blob'] = random.choice(blobs)

            return redirect('/display')

        else:
            session['successes'] = 0

            session['blob'] = random.choice(blobs)

            return render_template('wrong.html', successes=successes, blob_name=blob['name'])
    return render_template('display.html', image=get_single_image(blob['google_drive_id']), message=message, successes=successes, failed=True)




# include this for local dev
if __name__ == '__main__':
    app.run(debug=True)
 
    
