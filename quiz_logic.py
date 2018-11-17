# This is an extension of dojo_script_upgrade_classes.ipynb
# Using more object orientated approach, with quizzes also as objects

import glob, os, fnmatch
from random import sample, choice
import toml
import pdb
import gdrive_api_calls
import config
import io
import sys

# [{'underlined_name':'blah_blah','folder_name':'[blah][blah][blah]'}, ..., ...]
available_files = []

def get_category_options(available_files_with_categories):
    # input format: a list of diseases with format:
    # [{'underlined_name':'blah_blah','folder_name':'[blah][blah][blah]'}, ..., etc. ]
    
    available_category_options = {}

    # Create a blank list of categories
    for category,index in config.index_of_category_in_filename.items():
        available_category_options[category] = []

    # For each disease
    for disease in available_files_with_categories:
        # For each aspect of the disease
        for field, value in disease.items():
            # If the field is a category (rather than an ID or something else)
            if field in config.index_of_category_in_filename:
                # If value not already there:
                if value not in available_category_options[field] and value != '' and value != ' ':
                    # Assign the value of the category to the list for that category                
                    available_category_options[field].append(value)

    # output format:
    '''
    available_category_options = {'organ':organ_list, 
                'disease_type':disease_type_list, 
                'subtype':subtype_list, 
                'complexity':complexity_list, 
                'incidence':incidence_list,
                'name':name_list} 
                '''
    return available_category_options

def get_options_from_user(available_category_options):
    # Not used by app.py
    # input format:

    selected_category_options = {}

    '''
    available_category_options = {'organ':organ_list, 
                'disease_type':disease_type_list, 
                'subtype':subtype_list, 
                'complexity':complexity_list, 
                'incidence':incidence_list,
                'name':name_list} 
                '''

    # for each category
    for category, options in available_category_options.items():
        # Initialise selection for that category to an empty list
        selected_category_options[category] = []
        
        if category != 'name':
                
            # Get user inputs
            question = '''Of the options below, Please specify what you are interested in:
                            \n(To skip, press enter)
                            \n> '''
            user_input = None
            # While we haven't skipped
            while user_input != '':
                print(category, 'options:')
                for option in options:
                    print('\n\t'+option)
                # Ask the question
                user_input = str(input(question))
                # If valid
                if user_input in options:
                    # Record selection
                    selected_category_options[category].append(user_input)
                    # Allow loop to exit
                    user_input = ''



    # output format:
    '''
    selected_category_options = {'organ':organ_list, 
                'disease_type':disease_type_list, 
                'subtype':subtype_list, 
                'complexity':complexity_list, 
                'incidence':incidence_list,
                'name':name_list}
                '''
    return selected_category_options

def get_filenames_that_match(available_files,selected_category_options):
    # input format: list of available files and a dictionary of category selections

    # Accepts the dictionary of category options that were selected
    # Returns a list of all filenames that meet the criteria

    selected_files = []

    # For all files
    for file in available_files:
        # By default files are inlcluded
        definitely_out = False
        # For each category
        for category,selections in selected_category_options.items():
            # If the person made a selection
            if selections != [] and selections != ['']:
                # For the part of the filename relevant for this category
                # If the file category is not in the selections. 
                if file[category] not in selections:
                    definitely_out = True
        if not definitely_out:
            selected_files.append(file)

    # Shuffle
    shuffled_files = sample(selected_files,len(selected_files))


    # output format: list of files, same format as others but shorter
    return shuffled_files

def construct_quiz(selected_files,quiz_length,quiz_name):
    # input format: list of files, a number and string
        
    # Shuffle list
    shuffled_files = sample(selected_files,len(selected_files))

    # Remove the extras
    disease_shortlist = shuffled_files[:quiz_length]

    


    # Make a new quiz using this list of diseases
    fully_formed_quiz = Quiz(disease_shortlist, quiz_name)

    # output format:
    return fully_formed_quiz


def delete_all_files_in_cache_folder():
    pass
    '''
    # When a new session is started
    for file_present in os.scandir(google_drive_download_directory):        
        # Remove the file
        os.remove(google_drive_download_directory+file_present)
    '''


def coordinate_quiz(google_drive = False, first_time = False):
    # Called by directly as python file for local files
    # app.py will be calling these functions individually, not coordinate_quiz()

    

    '''
    1. Record files available in a list:
        - gdrive_api_calls.record_available_files()
        - Each file has characteristics, same for google drice and local files
        - Google drive files will have additional parameter the: drive ID
            - available_files = [{'underlined_name':'blah_blah',
                                            'folder_name':'[blah][blah][blah]'},
                                            'organ':'some_organ',
                                            'incidence':some_incidence,
                                            'name':some_name 
                                            ..., etc. ]
    '''
    if first_time:
        available_files = gdrive_api_calls.record_available_files(google_drive = google_drive)
        # Delete any files left around from previous sessions or users
        # If two users are using the app concurrenlty, this may destroy the cache of the other person.
        delete_all_files_in_cache_folder()

    '''
    3. Go through all the files and record the options available at each category
        - get_category_options()
    -     available_category_options = {'organ':organ_list, 
                'disease_type':disease_type_list, 
                'subtype':subtype_list, 
                'complexity':complexity_list, 
                'incidence':incidence_list,
                'name':name_list}                 
    '''
    
    available_category_options = get_category_options(available_files)

    # get number to quiz  
    try:
        max_quiz_length = int(input("\n(To skip, press enter)\nMaximum number of diseases in the quiz: "))
    except ValueError:
        print('(Defaulting to 5 elements)\n')
        max_quiz_length = 5
    '''
    4. Present the options to the user ask for selections
        - get_options_from_user()
        - selected_category_options = = {'organ':organ_list, 
                'disease_type':disease_type_list, 
                'subtype':subtype_list, 
                'complexity':complexity_list, 
                'incidence':incidence_list,
                'name':name_list}    
    '''
    selected_category_options = get_options_from_user(available_category_options)


    '''
    5. Go through all the files and eliminate files that the user excluded
        - check_for_filenames_by_category_selections()
        - selected_files = [{'underlined_name':'blah_blah',
                                            'folder_name':'[blah][blah][blah]'},
                                            'organ':'some_organ',
                                            'incidence':some_incidence,
                                            'name':some_name 
                                            ..., etc. ]
    '''
    selected_files = get_filenames_that_match(available_files,selected_category_options)
    

    '''
    
    6. Design a quiz based on selected folders
        - construct_quiz()

        
    '''

    
    fully_formed_quiz = Quiz(selected_files,max_quiz_length,google_drive = google_drive)


    '''
    7. Commence quiz
 
    '''
    # Step through the quiz
    fully_formed_quiz.step_through_quiz()
    

def download_file_using_id(google_drive_id):
    # TODO
    pass

class Disease():

    def __init__(self,disease_file,google_drive):
        
        self.file_details = disease_file
        self.using_google_drive = google_drive #True/False
        self.folder_name = disease_file["folder_name"]
        self.name = disease_file["printable_name"]   
        # Check if google_drive is used (True or False)
        if google_drive:
            self.google_drive_id = disease_file["google_drive_id"]
            # See if the file has been correctly cached, if not, download
            #self.check_file_download_status()
        else:
            self.content_directory = config.local_storage_directory                 

        
    def __repr__(self):
        return f'{self.name} with {len(self.images)} images'

    def __str__(self):
        return f'{self.name}'

    def take_subfile_inventory(self):
        # Calls google API to get the contents of this disease folder
        # Create a list containing the single dictionary for the accepting function
        file_of_interest = [self.file_details]
        self.details_and_subfiles = gdrive_api_calls.add_subfiles_to_file_details(file_of_interest, google_drive=True)[0]
        self.files_within_folder = self.details_and_subfiles['files_within_folder']  
        
        # Build a list of images
        images = []
        for file in self.files_within_folder:
            if file['subfile_type'] == 'image':
                images.append(file)
        shuffled_images = sample(images,len(images))
        self.images = shuffled_images
        try:
            self.current_image = self.images[0]
        except:
            self.current_image = None


    def read_text_file(self):
        # Returns the contents of a the google drive .txt file without downloading


        test_string = """
                        # can be multiline. Use backslashes at the end of a line to indicate new line. (\)
                        description = '''

                        Monomorphic cells with granular cytoplasm, with Crooke's Hyaline (intermediate filaments that aggregate around the nucleus as cytopathic response to ACTH). ACTH is sparsely granulated, which increases local recurrence risk. Crooke's adenoma has a high Ki-67 and all cells stain positive for ACTH.

                        '''

                        # must be one line, in format ihc = {ihc1='+',ihc2='-'}.
                        immunohistochemistry = {ACTH='+',Cam5.2='+',T-Pit='+'}

                        genetics = '''
                        T-Pit transcription factor
                        '''

                        # can be multiline, as strings separated by commas.
                        differentials = [
                        'pituitary_adenoma_densely_granulated_corticotroph',
                        'crookes_adenoma'
                        ]
                        """
        str_pres  = """

                    '# can be multiline.\r\ndescription = \'\'\'\r\nCell density higher than normal brain.\r\n\r\nMild to moderate nuclear pleomorphism.\r\n\r\nMonotony of atypical nuclei and irregular distribution indicates neoplasm.\r\n\r\n"naked nuclei" without recognizeable processes.\r\n\r\nNo prominent nucleolus.\r\n\r\nCytoplasm highly variable (even within the same tumour).\r\n\r\nIn normal CNS the cytoplasm blends within the neuropil.\r\n\r\nMitoses absent or very rare.\r\n\r\nMicrocystic spaces of the background (none to extensive).\r\n\r\nNo necrosis, no vascular proliferations.\r\n\r\nExcept radiation necrosis.\r\n\r\nLymphocytic cuffing (mostly in gemistocytic type)\r\n\r\nAbent to few rosenthal fibers.\r\n\r\n\r\n\'\'\'\r\n\r\n# must be one line, in format ihc = {ihc1=\'+\',ihc2=\'-\'}.\r\nimmunohistochemistry = {}\r\n\r\n# can be multiline, as strings separated by commas.\r\ndifferentials = [\r\n\r\n]\r\n'

                    """

        for file in self.files_within_folder:
                if file['subfile_type'] == 'text':
                    raw_contents = gdrive_api_calls.read_subfile(file)
                    
                    try:
                        contents = toml.loads(raw_contents)
                        self.text_file_contents = contents
                    except FileNotFoundError:
                        print('Error: could not load the .txt file')
                        self.text_file_contents = 'the text file has a typo'
                    except:
                        print(f'There are formatting errors in .txt file for: {file}')
                        self.text_file_contents = 'the text file has a typo'

        self.description = self.get_description()
        self.differentials = self.get_differentials()
        self.immunohistochemistry = self.get_immunohistochemistry()
        print('this code works')


    def download_non_image_files(self):
        # Caches files - to be deprecated
        for file in self.files_within_folder:
            if not file['subfile_type'] == 'image':
                gdrive_api_calls.download_subfile(file)

        self.text_file_contents = self.load_text_file() 
        self.description = self.get_description()
        self.differentials = self.get_differentials()
        self.immunohistochemistry = self.get_immunohistochemistry()
    
    def download_current_image(self):
        # To be deprecated
        gdrive_api_calls.download_subfile(self.current_image)
        # available in the folder: config.google_drive_download_directory
        # with filename self.current_image['temporary_file_name']

    def move_to_next_image(self):
        self.images.pop(0)
        self.current_image = self.images[0]

    def download_all_images(self):
        # To be deprecated
        # used to download all images after .take_subfile_inventory has been called.
        for image in self.images:
            gdrive_api_calls.download_subfile(image)

    def load_text_file(self):
        contents = {} # start with blank dictionary to populate with toml data

        if not self.using_google_drive:
            for file in os.listdir(self.content_directory+self.folder_name): 

                # if it is a text file
                if file.endswith('.txt') and not file.startswith('._') and not file.startswith('_'):                                        
                    try:
                        contents = toml.load(self.content_directory+self.folder_name+'/'+file) # load .txt as .toml
                    except FileNotFoundError:
                        print('Error: could not load the .txt file')
                    except:
                        print('There are formatting errors in the %s file'%(self.content_directory+self.folder_name+'/'+file))

        if self.using_google_drive:
            for file in self.files_within_folder:
                if file['subfile_type'] == 'text':
                    filename = file['temporary_file_name']
                    try:
                        contents = toml.load(config.google_drive_download_directory+filename)
                    except FileNotFoundError:
                        print('Error: could not load the .txt file')
                    except:
                        print(f'There are formatting errors in file: {filename}')
        return contents


    def get_list_of_images(self):
        images = []
        
        if not self.using_google_drive:
            for file in os.listdir(self.content_directory+self.folder_name): 
                if file.endswith(tuple(config.image_extensions)) and not file.startswith('._'):
                    images.append(file)
            if images == 0:
                print("(no images found for "+self.folder_name)
        
        if self.using_google_drive:
            for file in self.files_within_folder:
                if file['subfile_type'] == 'image':
                    images.append(file['temporary_file_name'])

        return images

            
    def get_description(self):
        description_text = []
        try:
            description_text = self.text_file_contents['description']
        except KeyError:
            print('(no description available)')        
            # for each file in the disease folder
        return description_text

    def get_clue(self):

        if not self.using_google_drive:
            split_name = self.folder_name.rsplit('[')
            hints = []
            for hint in split_name:
                if hint != '':
                    hints.append(hint.strip(']'))
            hints.pop()
            print(f'From the {hints[0]}, this is a {hints[1]} {hints[2]} thingy, considered a {hints[3]} and relatively {hints[4]}')
            return

        if self.using_google_drive:
            clue = 'No clues for you'
            return clue


    def show_all_images(self):
        
        pass

    def get_differentials(self):
        # This retrieves the differentials
        ddx_list = []
 
        try:
            ddx_list = self.text_file_contents['differentials']
        except KeyError:
            print('(no differentials available)')

        return ddx_list
    
    def display_differentials(self):
        # This prints the differentials out in a nice format
        if not self.using_google_drive:
            if len(self.differentials)==0:
                print("There are no differentials available")
            else:
                print(f'There are {len(self.differentials)} differentials, they are:')
                for individual_differential in self.differentials:
                    print(individual_differential)
                     
                
    def get_immunohistochemistry(self):
        ihc_dictionary = {}
        try:
            ihc_dictionary = self.text_file_contents['immunohistochemistry']
        except KeyError:
            print('(no ihc available)')
        return ihc_dictionary

    def display_immunohistochemistry(self):  
        
        if not self.using_google_drive:
            if self.immunohistochemistry=={}:
                print("No IHC available")

            for ihc_name in self.immunohistochemistry.items():
                print('The %s is %s'%(ihc_name, self.immunohistochemistry[ihc_name]))
        return

    def show_name_and_description(self):
        if not self.using_google_drive:
            print(f'Disease: {self.name}\n\n{self.description}')  
        return
        

    def get_folder_names_of_differentials(self):
        # Returns a list of folder names to be turned into a quiz

        differentials_quiz_length = len(self.differentials)
        
        print("Preparing differentials for "+self.name)

        ddx_folder_names = []
        if not self.using_google_drive:
            for differential in self.differentials:
                # Go through all disease names and select if they match.
                for disease in disease_folder_inventory:
                    # If the disease name in the inventory matches the name in the differentials
                    if disease["underlined_name"] == differential:
                        # add the full filename to the list. 
                        ddx_folder_names.append(disease["folder_name"])    
        if self.using_google_drive:
            print('need to get inventory of google drive and check for matches on differentials')

        return ddx_folder_names

    def check_file_download_status(self):
        # Check if each of the desired files has been cached and download if not
        print('about to download', self.files_within_folder)
        # For each subfile
        for file in self.files_within_folder:
            # If not cached
            if file['temporary_file_name'] not in config.google_drive_download_directory:
                # Download
                gdrive_api_calls.download_subfile(file)

class Quiz():
    # Creates quiz objects
            
    def __init__(self, list_of_eligible_folders, max_quiz_length, google_drive):
        # Make a list of disease files
        self.disease_files = self.shuffle_and_trim_diseases(list_of_eligible_folders,max_quiz_length)
        # Make a list of disease objects
        self.diseases = []
        for file in self.disease_files:
            # Check if desired folder name actually a disease             
            disease_as_object = Disease(file,google_drive)
            self.diseases.append(disease_as_object)
                
        # get quiz length
        self.total_quiz_length = len(self.disease_files)
        # Current progress. 1 = first disease
        self.progress = 1
        # remaining diseases
        self.remaining_diseases = self.diseases
        # A child quiz (nested quiz that has started mid-quiz)
        self.child_quiz = None
        # A parent quiz (a quiz that was paused to create this quiz)
        self.parent_quiz = None
        # Make name
        self.name = self.get_name()
        # Set a disease as the first element in the quiz
        self.current_disease = self.diseases[0]


    def __repr__(self):
        return f'"{self.name}" quiz with {self.total_quiz_length} items'

    def __str__(self):
        return f'"{self.name}" quiz, currently on disease {self.progress}/{self.total_quiz_length}'

    def shuffle_and_trim_diseases(self,list_of_eligible_folders,max_quiz_length):
        # Gets possible diseases and returns a shuffled list of the right length
        
        # Shuffle list
        shuffled_files = sample(list_of_eligible_folders,len(list_of_eligible_folders))

        # If no maximum
        if max_quiz_length == 0:
            disease_shortlist = shuffled_files
        else:
            # Remove the extras
            disease_shortlist = shuffled_files[:max_quiz_length]
        
        return disease_shortlist
    
    def get_name(self):
        # Creates a name to identify the quiz easily
        
        rank = ['hanshi','kaicho','kancho','kyoshi','master','meijin','mudansha','o-sensei','renshi','sempai','sensei','shihan','sosei','tashi','yudansha']
        thing = ['slide','frozen','haematoxylin','eosin','schiff','glass','recut','levels','of uncertain significance','cut up','formalin','decal','immuno','casette','membrane','nucleus','nucleolus','mitosis','chromatin','cytoplasm','grocott','congo red','trichrome','fite','reticulin','helicobacter']
        creatures = ['dragon kings','mermaids','bashe','golden adders','wasp queens','unicorns','amarok','bunyips','chtuhlu','night wolves','invisible swarms','sleeping hippopotami','honey bees','blue dinosaurs','giant pandas','peregrine falcons','baby wildebeest','battletoads','bionic cats','electric owls']

        name = f'{choice(rank).title()} {choice(thing).title()} and the {self.total_quiz_length} {choice(creatures).title()}'

        return name

    def move_to_next_disease(self):
        # This function sets the next disease up for quizzing
        if len(self.remaining_diseases)>1:
            # Get rid of the disease in index zero
            self.remaining_diseases = self.remaining_diseases.pop(0)
            # Set the new index 0 diseases as the current disease 
            self.current_disease = self.remaining_diseases[0]
        else:
            # End current quiz
            self.terminate_quiz()


    def clear_cached_files(self):
        pass
        '''
        # After a quiz has finished
        for file in self.content_directory:
            # Go through the files that were cached
            if file in self.list_of_cached_files:
                # Delete them from cache
                os.remove(self.content_directory+'file')
        '''

    def get_quiz_diseases(self):
        # Gives a list of what diseases are in this quiz
        names = []
        for disease in self.diseases:
            names.append(disease.name)
        return names

    def get_quiz_progress(self):
        # Returns current progress with cases done vs cases left
        print(f'Progress: Completed {self.progress} of {self.total_quiz_length} for quiz "{self.name}".')

    def start_a_nested_quiz(self):
        # In the event new differentials-based quiz was start this function ensures that the disease left behind is properly handled
        if len(self.current_disease.differentials)==0:
            return print('This disease has no differentials to base a new quiz on.')

        # Create a new quiz as a child of the current quiz
        self.child_quiz = Quiz(self.current_disease.get_folder_names_of_differentials,'Differentials quiz, started during {self.name} quiz.')
        
        # If the child quiz length is zero, cancel quiz
        if len(self.child_quiz.total_quiz_length):
            return print("No disease folders could be found to match recorded differentials")
        # Record the fact that this child quiz has a parent quiz, which is the current quiz. When we step through a quiz we will check for children and parents and display that.
        # 'my child's parent is me'
        self.child_quiz.parent_quiz = self
        # Go through child quiz
        self.child_quiz.step_through_quiz()
        # when done, display the current quiz name
        print('------\n------\n------\nNow returning to',self.current_disease)
        # Then display the current disease images
        self.current_disease.show_all_images()

    def terminate_quiz(self):
        # This is used to exit the current quiz, but it will not destroy any parent quizzes.
        self.remaining_diseases=[]

    def skip_answer(self):
        # This is a dummy function, so that the other elements in the options dictionary could be called with: option[value]().
        pass

    def ask_for_response(self):
        # Prompts a typed response
        response = str(input('Options: a for answer, i for ihc, d for ddx, ? for clue, e to explore differentials, q to quit, s to skip\n> '))

        return response

    def present_next_disease(self,disease):
        # Steps through the process of quizzing the user on a given disease
        print('DØJo!1------------------\n------DØJo!1------------\n------------DØJo!1------\n------------------DØJo!1')

        # check for parent quizzes, and note it's name so we know where we left off from.
        if self.parent_quiz is not None:
            print(f'This quiz has a parent quiz: ',self.parent_quiz,', which was paused to start the current quiz: self')
        
        # make the current disease available to other functions
        self.current_disease = disease

        options={'i':disease.display_immunohistochemistry, # property of disease
                'd':disease.display_differentials, # property of disease
                '?':disease.get_clue, # property of disease
                'e':self.start_a_nested_quiz, # quiz property
                'a':disease.show_name_and_description, # Print the answer -> print(f'The answer is: {disease.name}\n\n{disease.description}\n\n')
                'q':self.terminate_quiz, # property of the quiz       -> return self.remaining_diseases=[]
                's':self.skip_answer # prpoerty of the quiz        -> return                 
                }  
        options_where_we_repeat_the_question = ['i','d','?','c','v','','e']
        options_where_we_dont_need_to_see_the_answer = ['q','s']

        # Display images (Calls function of the disease to show_all_images)
        disease.show_all_images()
        # Ask for answers (Calls function of the disease to show_ask_for_answers)
        user_input = self.ask_for_response() # Here the person tries to answer, then sees the answer
        # evaluate responses

        while user_input in options_where_we_repeat_the_question:
            # Do the thing appropriate for the selection
            try:
                options[user_input]()
            except:
                pass
            # ask again
            user_input = self.ask_for_response()

        # Evaluate input    
        options[user_input]()   

        move_on_to_next_question = str(input('press any key to move to next question'))

        return

    def step_through_quiz(self):
        # This function steps through the quiz
        # Goes through the list to see what disease is next
        if len(self.remaining_diseases) == 0:
            print('thanks for playing')
            # Clear cache
            self.clear_cached_files()
            return

        for disease in self.remaining_diseases:
            self.present_next_disease(disease)

            # Removes the disease from the quiz
            self.remaining_diseases.remove(disease)
            # Increment progress counter
            self.progress+=1
            # Gets the progress of the quiz (get_quiz_progress) and prints the name of the current quiz
            self.get_quiz_progress()

            # If the quiz is at the end, ask the user if they want to design_new_quiz
            if self.progress == self.total_quiz_length:
                print('Finished quiz, need to implement option to start new quiz here')
                # Clear cache
                self.clear_cached_files()
                 
  

def unit_tests(test):

    if test == 1 or test == 'all':
        print('--------------------------------------------------------------------------')
        print('testing: gdrive_api_calls.record_available_files()')
        filenames = gdrive_api_calls.record_available_files(google_drive = False)
        for index,file in enumerate(filenames):
            
            if index < 2:
                for item,value in file.items():
                    print(f'The {item} is {value}\n\t\t')
    
    test_inventory = [{'folder_name': '[thyroid][malignant][tumour][spot_diagnosis][uncommon][papillary_thyroid_carcinoma_tall_cell_variant]', 'google_drive_id': None, 'organ': 'thyroid', 'disease_type': 'malignant', 'subtype': 'tumour', 'complexity': 'spot_diagnosis', 'incidence': 'uncommon', 'name': 'papillary_thyroid_carcinoma_tall_cell_variant', 'printable_name': 'papillary thyroid carcinoma tall cell variant'}
                    ,{'folder_name': '[thyroid][benign][inflammatory][spot_diagnosis][rare][de_quervains_thyroiditis]', 'google_drive_id': None, 'organ': 'thyroid', 'disease_type': 'benign', 'subtype': 'inflammatory', 'complexity': 'spot_diagnosis', 'incidence': 'rare', 'name': 'de_quervains_thyroiditis', 'printable_name': 'de quervains thyroiditis'}]

    if test == 2 or test == 'all':
        print('--------------------------------------------------------------------------')
        print('testing: get_category_options()')
        result = get_category_options(test_inventory)
        for key,value in result.items():
            print(f'The {key} is {value}')
        print(result)

    test_category_list_available = {'organ': ['thyroid', 'thyroid'], 'disease_type': ['malignant', 'benign'], 'subtype': ['tumour', 'inflammatory'], 'complexity': ['spot_diagnosis', 'spot_diagnosis'], 'incidence': ['uncommon', 'rare'], 'name': ['papillary_thyroid_carcinoma_tall_cell_variant', 'de_quervains_thyroiditis']}


    if test == 3 or test == 'all':
        print('--------------------------------------------------------------------------')
        print('testing: get_options_from_user()')
        result = get_options_from_user(test_category_list_available)
        print(result)

    test_category_list_selection = {'organ': [], 'disease_type': ['benign'], 'subtype': [], 'complexity': [], 'incidence': [], 'name': []}

    if test == 4 or test == 'all':
        print('--------------------------------------------------------------------------')
        print('testing: get_filenames_that_match()')
        result = get_filenames_that_match(available_files = test_inventory,
                                            selected_category_options = test_category_list_selection)
        print(result)

if __name__=="__main__":       
    # Start a new quiz, manually calling the inventory the first time only.

    #coordinate_quiz(google_drive = False, first_time = True)
    # Flask app should set google_drive to True

    #unit_tests(test=4)

        
    files = gdrive_api_calls.record_available_files(google_drive=True)
  
    for file in files:
        print('\n\n',files)


    
    
    
