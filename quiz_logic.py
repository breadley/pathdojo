# This is an extension of dojo_script_upgrade_classes.ipynb
# Using more object orientated approach, with quizzes also as objects

from PIL import Image
import glob, os, fnmatch
from random import sample
import toml
import tkinter as tk
import pdb

# Allowbale files to be read
image_extensions = ['.jpeg', '.jpg', '.bmp', '.tif', '.png', '.gif']

# The this file and the content_directory (which contains diseases) should be within one folder
content_directory = './folder_based_dojo/'
# Dictionary for diseases and their folder names {'disease':'foldername'}. Populated on start-up.

# [{'underlined_name':'blah_blah','folder_name':'[blah][blah][blah]'}, ..., ...]
disease_folder_inventory = []

# Goes through the list of folders and extracts items for each category from their name
def get_inventory():

    # USED ONLY FOR LOCAL / NON_GDRIVE application/testing

    # get all the files
    files = os.listdir(content_directory)

    return get_folder_tags(files)

def get_folder_tags(list_of_filenames):
    # This function takes a list of filenames
    # From either google drive or locally and returns separate lists
    # Of the different options available to choose from

    # for each file, append it's name elements to a new list
    organ_list = []
    disease_type_list = []
    subtype_list = []
    complexity_list = []
    incidence_list = []
    
  

    for disease in os.listdir(content_directory): # disease here is a folder name
        if disease.startswith('[') and disease.endswith(']'): # it's a disease
            category_list = disease.split('][')

            organ = category_list[0].strip('[')
            if organ not in organ_list and organ !='':
                organ_list.append(organ)

            disease_type = category_list[1].strip('[')
            if disease_type not in disease_type_list and disease_type !='':
                disease_type_list.append(disease_type)                        

            subtype = category_list[2].strip('[')
            if subtype not in subtype_list and subtype !='':
                subtype_list.append(subtype)

            complexity = category_list[3].strip('[')
            if complexity not in complexity_list and complexity !='':
                complexity_list.append(complexity)

            incidence = category_list[4].strip('[')
            if incidence not in incidence_list and incidence !='':
                incidence_list.append(incidence)      

            disease_name = category_list[5].strip(']')
            if disease_name !='':
                # Format: {disease_name:disease_folder_name}
                this_disease = {'underlined_name':disease_name,'folder_name':disease}
                disease_folder_inventory.append(this_disease)
                

    categories = {'organ_list':organ_list, 
                'disease_type_list':disease_type_list, 
                'subtype_list':subtype_list, 
                'complexity_list':complexity_list, 
                'incidence_list':incidence_list}            

    return categories
    


def get_options_from_folder_names(google_drive_folder_inventory):
    # This function is called by the app page where new quizzes are designed
    # Accepts the list of disease folders
    # [{'name':'blah blah','underlined_name':'blah_blah','google_drive_id':'id','folder_name':'blah'}]

    list_of_folder_names = []
    for folder in google_drive_folder_inventory:
        list_of_folder_names.append(folder['folder_name'])
    
    
    return get_folder_tags(list_of_folder_names)

class Disease():

    def __init__(self, disease_folder_name):
        self.folder_name = disease_folder_name 
        self.images = self.get_list_of_images()   
        self.text_file_contents = self.load_text_file()[0]
        self.name = self.load_text_file()[1]   
        self.description = self.get_description()
        self.differentials = self.get_differentials()
        self.immunohistochemistry = self.get_immunohistochemistry()
        
    def __repr__(self):
        return f'{self.name} with {len(self.images)} images'

    def __str__(self):
        return f'{self.name}'

    def load_text_file(self):
        contents = {} # start with blank dictionary to populate with toml data
        name = ''
        for file in os.listdir(content_directory+self.folder_name): 

            # if it is a text file
            if file.endswith('.txt') and not file.startswith('._') and not file.startswith('_'):                                        
                name = str(file).replace('.txt','')    
                try:
                    contents = toml.load(content_directory+self.folder_name+'/'+file) # load .txt as .toml
                except FileNotFoundError:
                    print('Error: could not load the .txt file')
                except:
                    print('There are formatting errors in the %s file'%(content_directory+self.folder_name+'/'+file))

        return contents, name


    def get_list_of_images(self):
        images = []
        for file in os.listdir(content_directory+self.folder_name): 
            if file.endswith(tuple(image_extensions)) and not file.startswith('._'):
                images.append(file)
        if images == 0:
            print("(no images found for "+self.folder_name)
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
        
        split_name = self.folder_name.rsplit('[')
        hints = []
        for hint in split_name:
            if hint != '':
                hints.append(hint.strip(']'))
        hints.pop()
        print(f'From the {hints[0]}, this is a {hints[1]} {hints[2]} thingy, considered a {hints[3]} and relatively {hints[4]}')

    def show_all_images(self):
        try:
            for image in self.images:
                image_to_display = Image.open(content_directory+self.folder_name+'/'+image)
                image_to_display.show()    
        except:
            print('no images to display')

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
        if self.immunohistochemistry=={}:
            print("No IHC available")

        for ihc_name in self.immunohistochemistry.items():
            print('The %s is %s'%(ihc_name, self.immunohistochemistry[ihc_name]))


    def show_name_and_description(self):
        print(f'Disease: {self.name}\n\n{self.description}')                      
        

    def get_folder_names_of_differentials(self):
        # Returns a list of folder names to be turned into a quiz

        differentials_quiz_length = len(self.differentials)
        
        print("Preparing differentials for "+self.name)

        ddx_folder_names = []
        
        for differential in self.differentials:
            # Go through all disease names and select if they match.
            for disease in disease_folder_inventory:
                # If the disease name in the inventory matches the name in the differentials
                if disease["underlined_name"] == differential:
                    # add the full filename to the list. 
                    ddx_folder_names.append(disease["folder_name"])    

        return dxx_folder_names

class Quiz():
    # Creates quiz objects

    def __init__(self,list_of_folder_names,quiz_name):
        # Make a list of disease objects
        self.diseases = []

        for disease_folder_name in list_of_folder_names: # TODO this fails when startig a differentials quiz.
            # Check if desired folder name actually a disease 
            for disease in disease_folder_inventory:
                # If the disease full folder name in our inventory matches the one in the list provided

                if disease["folder_name"] == disease_folder_name:                    
                    # Add the disease as a Disease object
                    disease_as_object = Disease(disease_folder_name)
                    self.diseases.append(disease_as_object)
 
                
        # create quiz name (if designed, call it those parameters, if ddx quiz, call it that)
        self.name = quiz_name
        # get quiz length
        self.total_quiz_length = len(list_of_folder_names)
        # Current progress. 1 = first disease
        self.progress = 1
        # remaining diseases
        self.remaining_diseases = self.diseases
        # A child quiz (nested quiz that has started mid-quiz)
        self.child_quiz = None
        # A parent quiz (a quiz that was paused to create this quiz)
        self.parent_quiz = None

    def __repr__(self):
        return f'"{self.name}" quiz with {self.total_quiz_length} items'

    def __str__(self):
        return f'"{self.name}" quiz, currently on disease {self.progress}/{self.total_quiz_length}'

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
        # This is used to exit the current quiz, but it will no destroy any parent quizzes.
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
        options_where_we_repeat_the_question = ['i','d','?','c','v','']
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
        if self.remaining_diseases == 0:
            print('thanks for playing')
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
            




def design_new_quiz(first_quiz=False):
    # THE FIRST HALF OF THIS WILL BE DEPRECATED IN FAVOUR OF OPTIONS AND BUTTONS
    # Asks for parameters and creates a quiz to meet those parameters
    # The quiz is then passed to the quiz executor (designed_quiz_preparer)

    # Take inventory of the categories available (only do this once)
    if first_quiz == True:
        categories = get_inventory()
        organ_list = categories['organ_list']
        disease_type_list = categories['disease_type_list']
        subtype_list = categories['subtype_list']
        complexity_list = categories['complexity_list']
        incidence_list = categories['incidence_list']
    

    # number to quiz  
    try:
        number_to_quiz = int(input("\n(To skip, press enter)\nMaximum number of diseases in the quiz: "))
    except ValueError:
        print('(Defaulting to 10 elements)\n')
        number_to_quiz = 10

    #[organ] skin, lung, brain
    print('Organs/systems available:')
    for option in organ_list:
        print('\n\t'+option)
    organ = str(input('''Please specify what you are interested in:
                        \n(To skip, press enter)
                        \nOrgan/system '''))
    while organ not in organ_list and organ != '':
            organ = str(input("\n(To skip, press enter)\n*Typo* Organ/sysem: "))
            
    
    #[type] inflammatory, benign_tumour, premalignant, malignant, congenital
    print('Disease types available:')
    for option in disease_type_list:
        print('\n\t'+option)
    disease_type = str(input("\n(To skip, press enter)\nDisease type: "))
    while disease_type not in disease_type_list and disease_type != '':
            disease_type = str(input("\n(To skip, press enter)\n*Typo* Disease type: "))
            
    
    #[subtype]     
    print('Subtypes available:')
    for option in subtype_list:
        print('\n\t'+option)
    subtype = str(input("\n(To skip, press enter)\nSubtype: "))
    while subtype not in subtype_list and subtype != '':
            subtype = str(input("\n(To skip, press enter)\n*Typo* Subtype: "))
            
    
    #[complexity] basic, advanced, spot_diagnosis, curiosity
    print('Complexities available:')
    for option in complexity_list:
        print('\n\t'+option)
    complexity = str(input("\n(To skip, press enter)\nComplexity: "))
    while complexity not in complexity_list and complexity != '':
            complexity = str(input("\n(To skip, press enter)\n*Typo* Complexity: "))
            
    
    #[incidence] common, uncommon (moderate), rare
    print('incidences available: ', incidence_list)
    for option in incidence_list:
        print('\n\t'+option)    
    incidence = str(input("\n(To skip, press enter)\nIncidence: "))
    while incidence not in incidence_list and incidence != '':
            incidence = str(input("\n(To skip, press enter)\n*Typo* incidence: "))

    
    # END DEPRECATION
    # 
    # 
            
    quiz_name = organ+disease_type+subtype+complexity+incidence
     
    # Get the parameters to search in the right order
    relevant_filenames = '[[]'+organ+'*'+disease_type+'*'+subtype+'*'+complexity+'*'+incidence+'[]]'

    # List of all diseases
    temp = os.listdir(content_directory)
     # shuffle the list to get a fresh quiz order
    shuffled_diseases = sample(temp, len(temp))
    # Filter out the ones that don't match our criteria
    filtered_diseases = fnmatch.filter(shuffled_diseases, relevant_filenames)

   
    # Only use the number of diseases we want to quiz
    selected_diseases = filtered_diseases[:number_to_quiz]

    # Make a new quiz using this list of diseases
    new_quiz = Quiz(selected_diseases, quiz_name)

    # Step through the quiz
    new_quiz.step_through_quiz()



if __name__=="__main__":        
    design_new_quiz(first_quiz=True)