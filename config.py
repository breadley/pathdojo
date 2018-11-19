class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'"\xe4\x7fTsrn[\xb7Vl\x94\xde\xaeQG'


class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class MyConfig(Config):
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'"\xe4\x7fTsrn[\xb7Vl\x94\xde\xaeQG'

# Allowbale files to be read
image_extensions = ['.jpeg', '.jpg', '.bmp', '.tif', '.png', '.gif']


# The location of the elements in the disease folder names
# [organ][disease_type][subtype][complexity][incidence][name - excluded here]
index_of_category_in_filename = {'organ':0,
                                'disease_type':1,
                                'subtype':2,
                                'complexity':3,
                                'incidence':4,
                                'name':5}

# This config.py file and these directories (which contains diseases) should be within one folder
# Where the disease folders are located when not using google drive
local_storage_directory = './folder_based_dojo/pathological_content/'

# Where files are downloaded to from google drive API
google_drive_download_directory = './static/'

# Google drive ID of the folder where the diseases are store. 
# This folder is special in that is has been shared with the service account email.
PATHOLOGICAL_CONTENT_FOLDER_ID = '10KMBdFqoGHkAQ_ywroaAsEQLue4NYEgv'

licenses = ['lp','lpn','qiao','hp','lpkayab','wp']