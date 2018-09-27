from flask import Flask, render_template, redirect, request, session
import config
import os
import gdrive_api_calls
import random

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')

# here is how we are handling routing with flask:
# Format {folder_name:ID,...}
dictionary_of_files = {}

def take_inventory():
    # This function creates a dictionary of files with name:ID combo from google drive

    # Get list from API using function that uses PyDrive
    temp_files = gdrive_api_calls.list_all_files('dummy_folder')
    for filename,id in temp_files.items():
        # if file is a disease folder with a correctly formatted name
        if file.os.startswith('[') and file.os.endswith(']'):
            # add file to globally acccessible list
            dictionary_of_files[filename] = id
        

def string_to_html_page(string):
    # This function takes a string to display and returns a HTML page.

    # render plain text nicely in HTML
    modified_string = string\
            .replace(" ","&nbsp;")\
            .replace(">","&gt;")\
            .replace("<","&lt;")\
            .replace("\n","<br>")
    # format page (monospace font so spaces align nicely for ASCII)
    page = "<html><body style='font-family: mono;'>" + modified_string + "</body></html>"

    return page
    


@app.route('/')
def index():
    # Homepage

    message = """   
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
    page = string_to_html_page(message)

    return page, 200

@app.route('/files/')
def files():
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

@app.route('/photos/',methods=['GET', 'POST'])
def photos():
    # Homepage/photos

    # Take inventory of files (ideally once only)
    take_inventory()
    blobs = []
    # Create a custom dictionary as a test for blob mania
    # Takes the inventory, and turns each name/id pair and makes them a list element
    # [{'name':'blah','google_drive_id':'id','folder_name':'blah','image_ids':['id1','id2','id3']}]
    for folder_name,google_drive_id in dictionary_of_files:
        this_blob={}
        this_blob['folder_name'] = folder_name
        this_blob['google_drive_id'] = google_drive_id
        this_blob['name'] = folder_name.strip(']').strip('*[')
        this_blob['image_ids'] = get_image_ids_from_folder(google_drive_id)

        blobs.append(this_blob)



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

    return render_template('index.html', image=blob['image'], successes=successes, failed=True)


'''
    count = 0
    photos = []
    for file,id in dictionary_of_files while count < 5:
        # Download the disease images and get list of images.
        disease_image_names_array = drive_api_calls.get_images(file,id)
        # display the image

        # Rmove the images
        clear_static_folder(disease_image_names_array)

        count+=1


'''

# include this for local dev
if __name__ == '__main__':
    app.run()
