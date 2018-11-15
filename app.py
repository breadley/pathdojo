from flask import Flask, render_template, redirect, request, session, url_for
import config
import os
import gdrive_api_calls
import random
import quiz_logic
import pdb
import json
from fuzzywuzzy import fuzz,process


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
        max_quiz_length = int(memory['quiz_length'])
        # Reset score counters      
        session['aggregate_score'] = 0
        session['this_score'] = None
        session['scored_disease'] = None
        session['scored_submission'] = None


        # If the submit button is pressed
        if selections['submit_button'] == 'pressed': 
            
            selected_files = quiz_logic.get_filenames_that_match(available_files,selected_category_options)
            
            if len(selected_files) > max_quiz_length:
                selected_files = selected_files[:(max_quiz_length)]
                print(selected_files)
                print(f'you wanted quiz length {max_quiz_length}, and we have prepared the quiz with length: {len(selected_files)}')

            # Memory for reviewing after the quiz
            diseases_for_review = []
            for disease in selected_files:
                diseases_for_review.append(disease['printable_name'])
            session['diseases_for_review'] = diseases_for_review

            session['total_quiz_length'] = len(selected_files)
            # Remove the last element, and assign as the current disease
            if len(selected_files)>1:
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
    ########## Disease things ##########
    differentials = ''
    immunohistochemistry = ''
    description = ''

    # Get disease information
    current_disease = session.get('current_disease',None)
    disease = quiz_logic.Disease(current_disease,google_drive=True)
    disease.take_subfile_inventory()

    # Need to replace this with in-memory IO (import IO)
    disease.download_non_image_files()
    # Use this instead ideally - butt cannot use toml.loads on the GetContentString() output from pydrive
    # So may have to save the file locally then delete
    # disease.read_text_file()
    

    images = disease.images
    image_ids = []
    for image in disease.images:
        image_ids.append(image['subfile_id'])

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



    ######### Scoring things ########
    current_quiz = session.get('current_quiz',None)
    aggregate_score = int(session.get('aggregate_score',0))
    quiz_length = int(session.get('total_quiz_length',None))
    number_completed = quiz_length - len(current_quiz['list_of_selected_files']) - 1
    if number_completed < 0:
        number_completed = 0

    points_available_for_whole_quiz = int(quiz_length*100) # points_available, # for visual bar
    points_obtained_so_far = int(aggregate_score) # points_obtained, # for visual bar
    points_missed_so_far = int(number_completed*100) - points_obtained_so_far

    print(f'''aggregate_score {aggregate_score}.\n \
            quiz_length {quiz_length}.\n \
            number_completed {number_completed}.\n \
            points_available_for_whole_quiz {points_available_for_whole_quiz}.\n\
            points_obtained_so_far {points_obtained_so_far}.\n\
            points_missed_so_far {points_missed_so_far}''')

    if aggregate_score != None and number_completed != 0:
        average_score = int(aggregate_score / (number_completed))
    else:
        average_score = 0

    scored_disease = session.get('scored_disease',None)
    this_score = session.get('this_score',None)
    scored_submission = session.get('scored_submission',None)



    if request.method == 'POST':
        print('request.form is: ',request.form)
        guess = request.form.get('guess') 
        if guess != '' and guess != None: # If a guess was typed in
            fuzz_score = fuzz.ratio(disease.name,guess)
            print(f'Your guess {guess} scored {fuzz_score} against {disease.name}')

            if aggregate_score == None:
                aggregate_score = 0
            session['aggregate_score'] = aggregate_score + fuzz_score
            session['this_score'] = fuzz_score
            session['scored_disease'] = disease.name
            session['scored_submission'] = guess

            # Save a single image id for review after the quiz
            images = list(session.get('images_for_later_review',[]))
            images.append(image_ids[0])
            session['images_for_later_review'] = images

        if request.form.get('move_on') == 'Next': # if the move on button has been primed
        
                # Get next item in quiz (pop)
            if len(current_quiz['list_of_selected_files']) == 0:
                
                diseases_for_review = session.get('diseases_for_review',[])
                images_for_later_review = session.get('images_for_later_review',[])

                print(f'dfr: {diseases_for_review}\niflr:{images_for_later_review}')
                
                return render_template('review.html', 
                        diseases_for_review = diseases_for_review,
                        images_for_later_review = images_for_later_review,
                        points_available_for_whole_quiz = points_available_for_whole_quiz, # points_available, # for visual bar
                        points_obtained_so_far = points_obtained_so_far, # points_obtained, # for visual bar
                        points_missed_so_far = points_missed_so_far, # points_missed, # for visual bar
                        this_score = this_score, # for banners
                        scored_disease = scored_disease, # for banners
                        average_score = average_score, # for banners
                        scored_submission = scored_submission) # for banners                
                #return redirect('/')
            
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
          

    # Pass the necessary values/dicts to the view page
    return render_template('view.html', 
                            points_available_for_whole_quiz = points_available_for_whole_quiz, # points_available, # for visual bar
                            points_obtained_so_far = points_obtained_so_far, # points_obtained, # for visual bar
                            points_missed_so_far = points_missed_so_far, # points_missed, # for visual bar
                            this_score = this_score, # for banners
                            scored_disease = scored_disease, # for banners
                            average_score = average_score, # for banners
                            scored_submission = scored_submission, # for banners
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
 
    
