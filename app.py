from flask import Flask, Response, json, request
import os
from pyfiglet import Figlet


app = Flask(__name__)

font = Figlet(font="starwars")

# here is how we are handling routing with flask:

@app.route('/')
def index():
    message = """   
                                                             . /  
                                                         . /  
                                                     . /  
                                                 . /  
                                             . /  
                                      _ .. /
                               /-__/   / /_)
                              /\/\   =/ = /_/         Hello there
                          . /    /  \,_\_)___(_
                      . /        \  /          \_
                  . /             \___\|\_,      /
             . /                       \__-\__    
        . /                              /\// '    
     /                                   (/_      /
                                        \_,\______|
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
    
    # render plain text nicely in HTML
    html_text = message\
            .replace(" ","&nbsp;")\
            .replace(">","&gt;")\
            .replace("<","&lt;")\
            .replace("\n","<br>")

    # use a monospace font so everything lines up as expected
    return "<html><body style='font-family: mono;'>" + html_text + "</body></html>", 200



# include this for local dev
if __name__ == '__main__':
    app.run()