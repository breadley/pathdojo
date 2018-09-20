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

# Goes through the list of folders and extracts items for each category from their name
def get_inventory():

    # get all the files
    files = os.listdir(content_directory)

    # for each file, append it's name elements to a new list
    organ_list = []
    disease_type_list = []
    subtype_list = []
    complexity_list = []
    incidence_list = []

    for disease in os.listdir(content_directory):
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
            
    return organ_list, disease_type_list, subtype_list, complexity_list, incidence_list   

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
        return 'Disease object',self.name

    def load_text_file(self):
        contents = {} # start with blank dictionary to populate with toml data
        name = ''
        for file in os.listdir(content_directory+self.folder_name): 

            # if it is a text file
            if file.endswith('.txt') and not file.startswith('._'):                                        
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
        print('There are %s differentials. They are:'%(len(self.differentials)))
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
        for ihc_name in self.immunohistochemistry:
            print('The %s is %s'%(ihc_name, self.immunohistochemistry[ihc_name]))
            
            
    def ask_for_answers(self):
        guess = str(input("*******************************\nYour answer is: "))

        if guess == '?':
            print('Here are some clues:\n\n')
            print(self.description)
            self.guess = str(input("*******************************\nYour answer is: "))
        elif guess == self.name:
            print('Correct! This is '+self.name)
        elif guess == 'q':
            return
        else:
            print('Correct answer: %s\n*******************************' %(self.name))
        print(self.description)        
        
        
    def differentials_challenge(self):
        # this starts a quiz based on the differential list of a disease

        # ----------------------------
        # This function will call the Quiz class to create a new quiz
        # e.g. new_quiz = Quiz(list_of_diseases)
        # return new_quiz
        # ----------------------------
        differentials_quiz_length = len(self.differentials)
        
        print("Starting a differentials quiz for "+self.name)

        count = 1

        for individual_differential in self.differentials:
            print('Differential %s of %s.'%(count,len(self.differentials)))
            # find the folder name 
            if folder.endswith(str(individual_differential)+']'):
                try:
                   # turn into a disease
                    individual_differential = Disease(folder)
                    individual_differential.show_all_images()
                    individual_differentials.ask_for_answers()
                except: # folder doesn't exist
                    print('cannot find differential: '+folder)
            count+=1
        for ddx_name in self.get_differentials():
                print(ddx_name)        


class Quiz():
    # Creates quiz objects

    def __init__(self,list_of_folder_names,quiz_name):
        # Make a list of disease objects
        self.diseases = []

        for disease_folder_name in list_of_folder_names:
            self.diseases.append(Disease(disease_folder_name))
        # create quiz name (if designed, call it those parameters, if ddx quiz, call it that)
        self.name = quiz_name
        # get quiz length
        self.total_quiz_length = len(list_of_folder_names)
        # Current progress. 1 = first disease
        self.progress = 1
        # remaining diseases
        self.remaining_diseases = self.diseases

    def __repr__(self):
        # Currently fails
       return str(self.name)

    def get_quiz_diseases():
        # Gives a list of what diseases are in this quiz
        names = []
        for disease in self.diseases:
            names.append(disease.name)
        return names

    def get_quiz_progress():
        # Returns current progress with cases done vs cases left
        print('Progress: Completed %s of %s for quiz "%s".'%(self.progress,self.total_quiz_length+self.name))
               

    def present_next_disease(next_disease):
        TODO
        # Gets the name of the next disease
         
        # Calls function of the disease to show_all_images
        
        # Calls function of the disease to show_ask_for_answers

        # Waits for keypress to get IHC, DDx's or even start a side-DDx_challenge

        pass

    def step_through_quiz():
        # This function steps through the quiz

        # Goes through the list to see what disease is next
        for disease in self.remaining_diseases:
            self.present_next_disease(disease)

            # Removes the disease from the quiz
            self.remaining_diseases.remove()
            # Increment progress counter
            self.progress+=1
            # Gets the progress of the quiz (get_quiz_progress) and prints the name of the current quiz
            self.get_quiz_progress()

            # If the quiz is at the end, ask the user if they want to design_new_quiz
            if self.progress == self.total_quiz_length:
                print('Finished quiz, need to implement new quiz here')

        
def designed_quiz_preparer(organ = '', disease_type = '', subtype = '', complexity = '', incidence = '', 
                   name = '', number_to_quiz = None):
    # This function will be destroyed once Quiz class implemented.

    
    for disease_folder_name in filtered_diseases: # for all diseases in the current directory           
       
        # if the disease matches the search
        if fnmatch.fnmatch(disease_folder_name, relevant_filenames) and disease_folder_name.startswith('[') and disease_folder_name.endswith(']'):    
            print ("""--------D-----------------------
                    \n-------------O------------------
                    \n------------------J-------------
                    \n-----------------------O--------""")
            disease = Disease(disease_folder_name)            
            disease.show_all_images()
            disease.ask_for_answers()
            #set_trace()   #for debugging
            key_press = {'i':disease.immunohistochemistry,
                         'd':disease.display_differentials,
                         'c':disease.differentials_challenge,
                        }    
            
            count += 1            

            print('%s cases completed. Quiz length: %s'%(count,number_to_quiz))
            if count == number_to_quiz:
                return

            looking_at_case = True
            
            while looking_at_case:
                post_answer_options = str(input('Press: Enter for next, d for ddx, c for ddx challenge, i for ihc, q to quit:'))
                
                if post_answer_options == 'q':  
                    looking_at_case = False
                    return
                elif post_answer_options == '': # enter gives ''
                    looking_at_case = False
                    break
                else:
                    try:
                        key_press[post_answer_options]() # the () executes the functions
                    except:
                        pass
            

def design_new_quiz(first_quiz=False):
    # Asks for parameters and creates a quiz to meet those parameters
    # The quiz is then passed to the quiz executor (designed_quiz_preparer)

    # Take inventory of the categories available (only do this once)
    if first_quiz == True:
        organ_list, disease_type_list, subtype_list, complexity_list, incidence_list  = get_inventory()
    

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
    pdb.set_trace()
    # Step through the quiz
    new_quiz.step_through_quiz()

# An example dynamically adjusting tkinter window with blocks
class DynamicGrid(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.text = tk.Text(self, wrap="char", borderwidth=0, highlightthickness=0,
                            state="disabled")
        self.text.pack(fill="both", expand=True)
        self.boxes = []

    def add_box(self, color=None):
        bg = "blue"
        box = tk.Frame(self.text, bd=1, relief="sunken", background=bg,
                       width=100, height=100)
        self.boxes.append(box)
        self.text.configure(state="normal")
        self.text.window_create("end", window=box)
        self.text.configure(state="disabled")

class Window(object):
    def __init__(self):
        self.root = tk.Tk()
        self.dg = DynamicGrid(self.root, width=500, height=200)
        add_button  = tk.Button(self.root, text="Add", command=self.dg.add_box)

        add_button.pack()
        self.dg.pack(side="top", fill="both", expand=True)

        # add a few boxes to start
        for i in range(10):
            self.dg.add_box()

    def start(self):
        self.root.mainloop()






if __name__=="__main__":    
    #Window().start()
    design_new_quiz(first_quiz=True)