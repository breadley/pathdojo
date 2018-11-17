from flask import Flask, render_template, redirect, request, session, url_for
import config
import os
import gdrive_api_calls
import random
import quiz_logic
import pdb
import json
from fuzzywuzzy import fuzz,process

# Note that in aws lambda, os.chdir('/tmp') gets you to '/tmp', but on MacOS you end up in '/private/tmp'
original_path = os.getcwd()
os.chdir('/tmp')
PATH_TO_TEMP_DIRECTORY = os.getcwd()
os.chdir(original_path)

app = Flask(__name__, static_url_path = PATH_TO_TEMP_DIRECTORY, static_folder = PATH_TO_TEMP_DIRECTORY)
app.config.from_object('config.MyConfig')
# Debug mode on/True or off/False
app.debug=False

 
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
    
    selections = {}

    # If a button is pressed
    if request.method == 'POST':
        selections = request.form.to_dict()
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

            # Memory for reviewing after the quiz
            diseases_for_review = []
            # Forget the images from the last quiz
            session['images_for_later_review'] = []
            for disease in selected_files:
                diseases_for_review.append(disease['printable_name'])            
            session['diseases_for_review'] = diseases_for_review

            session['total_quiz_length'] = len(selected_files)
            # Remove the last element, and assign as the current disease
            if len(selected_files)>1:
                session['current_disease'] = selected_files.pop()                  
            else:
                session['current_disease'] = selected_files[0]
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
          
            return redirect(url_for('view'))
    
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
    list_of_downloaded_image_names = []
    for image in images:
        image_id = image['subfile_id']
        download_name = image['temporary_file_name']
        download_folder, downloaded_file_name = gdrive_api_calls.download_an_image(file_id = image_id,file_name=download_name)
        list_of_downloaded_image_names.append(downloaded_file_name)

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
            aggregate_score = aggregate_score + fuzz_score
            session['aggregate_score'] = aggregate_score
            this_score = fuzz_score
            session['this_score'] = this_score
            scored_disease = disease.name 
            session['scored_disease'] = scored_disease
            scored_submission = guess
            session['scored_submission'] = scored_submission

            # Save a single image id for review after the quiz
            images = list(session.get('images_for_later_review',[]))
            images.append(list_of_downloaded_image_names[0])
            session['images_for_later_review'] = images

        if request.form.get('move_on') == 'Next': # if the move on button has been primed
        
                # Get next item in quiz (pop)
            if len(current_quiz['list_of_selected_files']) == 0:
                session['current_disease'] = None
                diseases_for_review = session.get('diseases_for_review',[])
                images_for_later_review = session.get('images_for_later_review',[])

                print(f'dfr: {diseases_for_review}\niflr:{images_for_later_review}')
                
                # Update scores for review page.
                points_obtained_so_far = aggregate_score
                points_missed_so_far = points_available_for_whole_quiz - points_obtained_so_far
                average_score = aggregate_score / quiz_length


                
                original_path = os.getcwd()
                os.chdir('/tmp')
                for image in list_of_downloaded_image_names:
                    while image not in os.listdir('.'):
                        print('downloading', image)
                os.chdir(original_path)
                

                return render_template('review.html', 
                        diseases_for_review = diseases_for_review,
                        images_for_later_review = images_for_later_review,
                        points_available_for_whole_quiz = points_available_for_whole_quiz, # points_available, # for visual bar
                        points_obtained_so_far = points_obtained_so_far, # points_obtained, # for visual bar
                        points_missed_so_far = points_missed_so_far, # points_missed, # for visual bar
                        this_score = this_score, # for banners
                        scored_disease = scored_disease, # for banners
                        average_score = average_score, # for banners
                        scored_submission = scored_submission) #! for banners                
                
            
            # Get the old list, remove the last element and assign as current disease
            session['current_disease'] = current_quiz['list_of_selected_files'].pop()
            
            # update current quiz
            session['current_quiz'] = current_quiz



        if request.form.get('skip_option') == 'skipping':
            # Remove the last element from the quiz, and assigne it as the current disease
            session['current_disease'] = current_quiz.pop()
            print('we are skipping this disease')

        return redirect(url_for('view'))

    
    original_path = os.getcwd()
    os.chdir('/tmp')
    for image in list_of_downloaded_image_names:
        while image not in os.listdir('.'):
            print('downloading', image)
    os.chdir(original_path)
    

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
                            list_of_downloaded_image_names = list_of_downloaded_image_names,
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


# include this for local dev
if __name__ == '__main__':
    app.run(debug=True)
 
    
