
import random
import pdb
import quiz_logic
import config


from google.oauth2 import service_account
import googleapiclient.discovery
import os, tempfile, zipfile, pprint, io 
from random import sample
import toml
from contextlib import contextmanager
import requests
from googleapiclient.http import MediaIoBaseDownload



SERVICE_ACCOUNT_FILE = 'service_account_credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'


credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

@contextmanager
def temporary_work_dir():
    # Inspiration to download images to temp file in AWS lambda
    # https://stackoverflow.com/questions/48364250/write-to-tmp-directory-in-aws-lambda-with-python
    # USAGE:
	# with temporary_work_dir():
	# 	DO ANYTHING HERE
	# Then by here the temp file will have been deleted

	old_work_dir = os.getcwd()
	with tempfile.TemporaryDirectory() as tmp_dir:
		os.chdir(tmp_dir)
		try:
			yield
		finally:
			os.chdir(old_work_dir)

# Auto-iterate through all files that matches this query
def list_all_files(folder): # Eventually deprecate
	file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
	results = {}
	for file1 in file_list:
		if file1['title'].startswith('['):
			results[file1['title']] = file1['id']
	return results

def record_available_files(google_drive=False): 
	# Using the service account
	# input format: No input data required. Google drive is true/false
	# output format:
	# available_files = [{'underlined_name':'blah_blah','folder_name':'[blah][blah][blah]'}, ..., etc. ]
	
	page_token = None
	   
	# Clear global inventory
	available_files = []
		
	
	query = f"'{config.PATHOLOGICAL_CONTENT_FOLDER_ID}' in parents" # Only get files where this folder is the parent
	while True:
		response = drive.files().list(q=query,
										fields='nextPageToken, files(id, name)',
										pageToken=page_token).execute()
		for file in response.get('files', []):
			folder_name = file.get('name')
			google_drive_id = file.get('id')
			
			# If a completed disease folder
			if folder_name.startswith('[') and folder_name.endswith(']'): 				
				this_disease={}
				this_disease['folder_name'] = folder_name
				this_disease['google_drive_id'] = google_drive_id             
				
				# get {'full_name':'','organ':'','disease_type':'', etc.}
				filename_dict = filename_breakdown(folder_name)
				for category,value in filename_dict.items():
					this_disease[category] = value
				
				this_disease['printable_name'] = ''
				for letter in this_disease['name']:
					if letter == '_':
						this_disease['printable_name']+=' '
					else:
						this_disease['printable_name']+=letter

				available_files.append(this_disease)

		page_token = response.get('nextPageToken', None)
		if page_token is None:
			break	
	
	# output format:
	# available_files = [{'underlined_name':'blah_blah','folder_name':'[blah][blah][blah]'}, ..., etc. ]
	return available_files

def add_subfiles_to_file_details(list_of_files, google_drive=False):
	# This takes a list (a short list of the diseases of interest)
	# Looks at the contents of the files and adds the important details to the file record
	# Returns the same list but with the additional details included
	# Google drive is True/False
	# This could probably be optimised by making specialised queries to the google drive API if needed


	list_of_files_including_subfiles = []

	for main_file in list_of_files:
		google_drive_id = main_file['google_drive_id']
		page_token = None
		files_inside = []

		while True:
			response = drive.files().list(q=f"'{google_drive_id}' in parents and trashed=false",
												fields='nextPageToken, files(id, name, webContentLink)',
												pageToken=page_token).execute()
			for file in response.get('files', []):
				subfile = file.get('name')
				subfile_id = file.get('id')
				
				
				# If the file is a valid file
				if not subfile.startswith('.') and not subfile.startswith('_'):
					this_file = {}

					subfile_name,subfile_extension = os.path.splitext(subfile)
					subfile_name = subfile_name.lower()
					subfile_extension = subfile_extension.lower()
					this_file = {}
					this_file['subfile_name'] = subfile
					this_file['subfile_id'] = subfile_id
					this_file['subfile_extension'] = subfile_extension
					this_file['temporary_file_name'] = 'temporary_file_with_id_'+subfile_id + subfile_extension
					this_file['subfile_url'] = file.get('webContentLink')

					if subfile_extension in config.image_extensions:
						this_file['subfile_type']='image'
					if subfile_extension == '.xml':
						this_file['subfile_type']='xml'
					if subfile_extension == '.toml' or subfile_extension == '.txt':
						this_file['subfile_type']='text'

					files_inside.append(this_file)			

			page_token = response.get('nextPageToken', None)
			if page_token is None:
				break
			
		# Record list of files
		main_file['files_within_folder'] = files_inside

		list_of_files_including_subfiles.append(main_file)

	return list_of_files_including_subfiles




def filename_breakdown(filename): # FINISHED
	# Accepts a filename as a string: 'blah'
	# Returns a dictionary of values about the name

	parts = {}
	components = []
	for segment in filename.split('['):
		if segment != '':
			components.append(segment.strip(']'))
	
	for category,index in config.index_of_category_in_filename.items():
		parts[category] = components[index]
	
	# output format:
	# parts =  {'full_name':'','organ':'','disease_type':'', etc.}
	return parts


def get_file_ids_from_folder(folder_id):
	# TO BE DEPRECATED IN FAVOUR OF add_subfiles_to_file_details
	# Returns an array of ids for the images within a given folder
	image_ids = []
	config.image_extensions = ['.jpeg', '.jpg', '.bmp', '.tif', '.png', '.gif']
	
	# Also returns a list containing the google drive id of any .txt files within a given folder
	# Usually would have only one file
	text_file_ids = []

	# Create a pydrive object for the folder
	folder = drive.CreateFile({'id':folder_id})
	# List the contents of the folder
	content_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()

	for file in content_list:

		file_title = file['title']
		file_id = file['id']
		if file_title.endswith(tuple(config.image_extensions)) and not file_title.startswith('._'):
			image_ids.append(file_id)
		if file_title.endswith('.txt') and not file_title.startswith('._'):
			text_file_ids.append(file_id)
	return image_ids, text_file_ids


def select_an_image_from_list_of_ids(image_id_list):
	# Used to download a single image and return the location for dispaying
	
	# If the list is empty, return a photo of the ocean
	if image_id_list == [] or image_id_list == None:
		filename = 'empty.jpeg'
		file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
		for file1 in file_list:
			if file1['title']==filename:
				 # test case '1vmTwm2W-8btmifsBG1mkOlvspwkdEW-8'
				image_id_list.append(file1['id'])
				image_id_list.append(file1['id'])
				
	
	# pick random id
	random_id = random.choice(image_id_list)
	# create pydrive object
	image = drive.CreateFile({'id':random_id})
	filename = f'temporary_image_with_id_{random_id}.jpeg'
	# download image
	image.GetContentFile('static/'+filename)
	
	return filename,id

def read_subfile(subfile):
	# Accepts the dictionary of the object

	# Create pydrive object
	file = drive.CreateFile({'id':subfile['subfile_id']})
	content = file.GetContentString()
	return content


def download_subfile(subfile):
	# Accepts the dictionary of the object of the text file and loads as toml
	# Downloads the .txt file to the temporary folder, for deletion by default
	# Returns file content as toml dictionary
    # https://developers.google.com/drive/api/v3/manage-downloads
    
	file_id = subfile['subfile_id']
	temp_name = subfile['temporary_file_name'] # includes extension
	file_contents = {}

	request = drive.files().get_media(fileId=file_id)
	with temporary_work_dir():
		# This causes files to be saved in a nested folder within /tmp or /private/tmp
		
		fh = io.FileIO(temp_name,'wb')
		downloader = MediaIoBaseDownload(fh, request)
		done = False
		while done is False:
			status, done = downloader.next_chunk()
		try:
			file_contents = toml.load(temp_name)
		except:
			print('Fail to load a toml file from', temp_name)
			pass

	return file_contents 

def download_an_image(file_id = '',file_name='one_big_image'):
	# Downloads an image to the '/tmp' folder, which lambda keeps for about ten minutes
    # https://developers.google.com/drive/api/v3/manage-downloads
    
    request = drive.files().get_media(fileId=file_id)

    file_name = file_id + '_' + file_name

    # Change to temp directory
    old_work_dir = os.getcwd()
    os.chdir('/tmp')

    fh = io.FileIO(file_name,'wb') # changed from io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    image_folder = os.getcwd()

    # Change back to original directory

    os.chdir(old_work_dir)

    return image_folder, file_name

def get_images(folder_id):
	# DEPRECATED
	# Returns an array of image names of downloaded images (temporary)
	# Format ['static/image_index','static/image_index']

	# Create a pydrive object for the folder
	folder = drive.CreateFile({'id':folder_id})
	# List the contents of the folder
	content_list = folder.drive.ListFile(folder).GetList()
	
	image_object_arrary = []
	# Go through folder
	for index,file in enumerate(content_list):
		
		# Turn the file into an object
		image = drive.CreateFile({'id':file['id']})
		# Download the image as a temp file with an index
		image.GetContentFile(f'static/temporary_image_{index}')
		# record the indexes/names
		image_object_arrary.append(f'static/temporary_image_{index}')
	
	return image_object_arrary


if __name__=='__main__':
	pass



