from flask import Flask, Response, json, request
import os
import gdrive_api_calls

app = Flask(__name__)

# here is how we are handling routing with flask:

dictionary_of_files = {}

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
    answer = str(input("What can we do here?"))
    return page, 200

@app.route('/files/')
def files():
    # Homepage/files
    content = ''
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

@app.route('/photos/')
def photos():
    # Homepage/photos

    count = 0
    photos = []
    for file,id in dictionary_of_files while count < 5:
        #Need to implement this method
        #gdrive_api_calls.get_photo(file,id)
        count+=1




# include this for local dev
if __name__ == '__main__':
    app.run()
