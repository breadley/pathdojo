from flask import Flask, render_template, redirect, request, session
import config
import os
import gdrive_api_calls
import random

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')

# here is how we are handling routing with flask:
# Format {folder_name:ID,...}
list_of_files_with_attibutes = []
# Inventory needs to only be taken once
need_to_take_inventory = True

dojo_welcome = """   
                                                         . /  
                                                     . /  
                                                 . /  
                                             . /  
                                         . /  
                                     . /
                               /-__/   / /_)
                              /\/\   =/ = /_/         Hello there
                                 /  \,_\_)___(_
                                 \  /    .  .  \_
                                  \___\|\_,   .  /
                                        \__-\__  .  
                                         /\// '   . 
                                         (/_   .  /
                                        \_,\__.___|
                                       __#######]
                                    __/._  .  . )
                                  _/ .\  .   . <
                                 \.    .   . _/
                                 /\__.  _.__/  
                                (    \_/ (   /_|
                                 )/_     /'-`_) 
                                  |     /  (___'_)
                                  '/. __)
                              ..   \_/ |          . 
                                    _\ (    . ..
                                 (____`_)    



                        You and Pathdojo form a symbiont circle.

                        What happens to one of you will affect the other. 
                        
                        You must understand this.     
                        """


def take_inventory():
    # This function creates a dictionary of files with attributes 
    # IDs are from google drive

    # [{'name':'blah','google_drive_id':'id','folder_name':'blah','image_ids':['id1','id2','id3']}]

    # Get list from API using function that uses PyDrive
    for folder_name,google_drive_id in gdrive_api_calls.list_all_files('dummy_folder').items():
        # Create disease attributes
        this_disease={}
        this_disease['folder_name'] = folder_name
        this_disease['google_drive_id'] = google_drive_id
        this_disease['name'] = folder_name.strip(']').strip('*[')
        # do these only when needed, not for every photo
        #this_disease['image_ids'] = gdrive_api_calls.get_file_ids_from_folder(google_drive_id)[0]
        #this_disease['text_file'] = gdrive_api_calls.get_file_ids_from_folder(google_drive_id)[1]  


        # Add to globally addressable list
        list_of_files_with_attibutes.append(this_disease)

def string_to_html(string):
    modified_string = string\
            .replace(" ","&nbsp;")\
            .replace(">","&gt;")\
            .replace("<","&lt;")\
            .replace("\n","<br>")
    return modified_string

    
'''
@app.route('/')
def index():
    # Homepage    
    
    page = "<html><body style='font-family: mono;'>" + string_to_html(dojo_welcome) + "</body></html>"

    return page, 200
'''



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
        if file.os.startswith('[') and file.os.endswith(']'):
            # add file to globally acccessible list
            dictionary_of_files[filename] = id
            content+=f'\n\nFilename: {filename}\t\t\tFile ID: {id}'
    

    page = string_to_html_page(content)

    # use a monospace font so everything lines up as expected
    return page, 200   

def get_single_image(blob_folder_drive_id):
    # This function randomly chooses an image from a blob's folder and downloads it for display

    # Get image id's
    blob_folder_image_ids = gdrive_api_calls.get_file_ids_from_folder(blob_folder_drive_id)[0] # 1 is for text, 0 for images
    # Download a single image
    random_image_filename = gdrive_api_calls.select_an_image_from_list_of_ids(blob_folder_image_ids)[0]
    random_image_id = gdrive_api_calls.select_an_image_from_list_of_ids(blob_folder_image_ids)[1]
    return random_image_filename


@app.route('/',methods=['GET', 'POST'])
def index():
    # Intro message TODO


    # Take inventory of files (ideally once only)
    '''
    if need_to_take_inventory:
        take_inventory()
        need_to_take_inventory=False
    '''
    take_inventory()

    # Reference the diseases as blobs for testing
    # blobs = list_of_files_with_attibutes

    # a temporary list for testing
    a_few_blobs = {'[thyroid][malignant][tumour][spot_diagnosis][common][papillary_thyroid_carcinoma]': '1m1PUfDjppvv9fs1H9P6M4__qcY-s5vES', 
    '[lung][malignant][tumour][spot_diagnosis][uncommon][papillary_adenocarcinoma_of_the_lung]': '1FRdtTWqmmuDSZkkfVRD5JcWn4OR8M4cL',
    '[head_neck][benign][][spot_diagnosis][rare][fibrous_dysplasia]': '1e38fh5DdeB6q28MxU0GNiwEkeuDB6wuK'}
    # Temporary tiny blob list preparation
    blobs = []    
    for folder_name,google_drive_id in a_few_blobs.items():
        # Create disease attributes
        this_disease={}
        this_disease['folder_name'] = folder_name
        this_disease['google_drive_id'] = google_drive_id
        this_disease['name'] = folder_name.strip(']').strip('*[')
        #this_disease['image_ids'] = gdrive_api_calls.get_file_ids_from_folder(google_drive_id)[0]
        #this_disease['text_file'] = gdrive_api_calls.get_file_ids_from_folder(google_drive_id)[1]
        blobs.append(this_disease)  


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

            return redirect('/')

        else:
            session['successes'] = 0

            session['blob'] = random.choice(blobs)

            return render_template('wrong.html', successes=successes, blob_name=blob['name'])
    return render_template('index.html', image=get_single_image(blob['google_drive_id']), successes=successes, failed=True)


# include this for local dev
if __name__ == '__main__':
    app.run()
    
