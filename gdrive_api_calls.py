from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import random
import os
import pdb

gauth = GoogleAuth()

# TODO: This seems to be for single app use, not server deployment. 
# I believe for real world deployment we just get rid of it
# As per https://pythonhosted.org/PyDrive/quickstart.html
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

index_of_category_in_filename = {'organ':0,
                                'disease_type':1,
                                'subtype':2,
                                'complexity':3,
                                'incidence':4,
                                'name':5}

content_directory = './folder_based_dojo/'

# Allowbale files to be read
image_extensions = ['.jpeg', '.jpg', '.bmp', '.tif', '.png', '.gif']



# Auto-iterate through all files that matches this query
def list_all_files(folder): # Eventually deprecate
	file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
	results = {}
	for file1 in file_list:
		if file1['title'].startswith('['):
			results[file1['title']] = file1['id']
	print(f'There are currently {len(results)} files in the Google Drive folder')
	return results

def record_available_files(google_drive=False): # FINISHED
	# input format: No input data required. Google drive is true/false
	# output format:
	# available_files = [{'underlined_name':'blah_blah','folder_name':'[blah][blah][blah]'}, ..., etc. ]

	# Temporary variable
	unprocessed_files = []    
	# Clear global inventory
	available_files = []

	# if local files, record the files in dictionary format
	if not google_drive: 
		for file in os.listdir(content_directory):
			# A dictionary where the google drive ID is None
			this_file = {}
			this_file['filename'] = file
			this_file['id'] = None
			unprocessed_files.append(this_file)

	# if google drive
	else:
		drive_files = drive.ListFile({'q': "'root' in parents"}).GetList()
		for file in drive_files:
			this_file = {}
			this_file['filename'] = file['title']
			this_file['id'] = file['id']
			unprocessed_files.append(this_file)

	# Go through the list of folders
	for file in unprocessed_files:
		folder_name = file['filename']
		google_drive_id = file['id']

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
	
	
	# output format:
	# available_files = [{'underlined_name':'blah_blah','folder_name':'[blah][blah][blah]'}, ..., etc. ]
	return available_files

def add_subfiles_to_file_details(list_of_files, google_drive=False):
	# This takes a list (a short list of the diseases of interest)
	# Looks at the contents of the files and adds the important details to the file record
	# Returns the same list but with the additional details included
	# Google drive is True/False
	list_of_files_including_subfiles = []

	for main_file in list_of_files:
		google_drive_id = main_file['google_drive_id']

		# Record subfiles within each folder
		unprocessed_subfiles = []
		files_inside = []

		# Compile a list of files and IDs (none where local files)
		if google_drive:
			# List the contents of the folder
			drive_subfiles = drive.ListFile({'q': f"'{google_drive_id}' in parents and trashed=false"}).GetList()
			for file in drive_subfiles:
				this_file = {}
				this_file['filename'] = file['title']
				this_file['id'] = file['id']
				unprocessed_subfiles.append(this_file)

		if not google_drive:
			for file in os.listdir(content_directory+folder_name):
				this_file = {}
				this_file['filename'] = file
				this_file['id'] = None
				unprocessed_subfiles.append(this_file)	
		
		# For all of the files within the disease folder
		for file in unprocessed_subfiles:
			subfile = file['filename']
			subfile_id = file['id']
			# If the file is a valid file
			if not subfile.startswith('.') and not subfile.startswith('_'):
				subfile_name,subfile_extension = os.path.splitext(subfile)
				this_file = {}
				if subfile_extension in image_extensions:
					this_file['image_name']=subfile
					this_file['image_id'] = subfile_id
				if subfile_extension == '.xml':
					this_file['xml_name']=subfile
					this_file['xml_id'] = subfile_id
				if subfile_extension == '.toml' or subfile_extension == '.txt':
					this_file['textfile_name']=subfile
					this_file['textfile_id'] = subfile_id
				files_inside.append(this_file)
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
	
	for category,index in index_of_category_in_filename.items():
		parts[category] = components[index]
	
	# output format:
	# parts =  {'full_name':'','organ':'','disease_type':'', etc.}
	return parts


def get_file_ids_from_folder(folder_id):
	# TO BE DEPRECATED IN FAVOUR OF add_subfiles_to_file_details
	# Returns an array of ids for the images within a given folder
	image_ids = []
	image_extensions = ['.jpeg', '.jpg', '.bmp', '.tif', '.png', '.gif']
	print('Getting the files from within one folder...')
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
		if file_title.endswith(tuple(image_extensions)) and not file_title.startswith('._'):
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
		# Print the files
		print('title: %s, id: %s' % (file['title'], file['id']))
		# Turn the file into an object
		image = drive.CreateFile({'id':file['id']})
		# Download the image as a temp file with an index
		image.GetContentFile(f'static/temporary_image_{index}')
		# record the indexes/names
		image_object_arrary.append(f'static/temporary_image_{index}')
	
	return image_object_arrary

def clear_static_folder(list_of_images_to_be_destroyed):
	# Clears a set of images in 'static' folder, once they are no longer needed
	# Accepts list in format ['static/image_index','static/image_index']

	# Go through files we have
	for file_present in os.scandir('/static'):
		# If we find a match
		if file_present in list_of_images_to_be_destroyed:
			# Remove the file
			os.remove(f'/static{file_present}')
	return

if __name__=='__main__':
	pass






''' Examples
{'folder_name': '[thyroid][malignant][tumour][spot_diagnosis][uncommon][medullary_thyroid_carcinoma]', 
				'google_drive_id': '1VujLlAbRwLhGDMGncW9M22tNc270Nhqi', 
				'organ': 'thyroid', 
				'disease_type': 'malignant', 
				'subtype': 'tumour', 
				'complexity': 'spot_diagnosis', 
				'incidence': 'uncommon', 
				'name': 'medullary_thyroid_carcinoma', 
				'printable_name': 'medullary thyroid carcinoma', 
				'files_within_folder': [{'textfile_name': 'medullary_thyroid_carcinoma.txt', 'textfile_id': '1CG_gfgNuP43wwoWWG6_5PCKdURXhH4E6'}, 
										{'image_name': 'lp9.jpg', 'image_id': '1JAhCtAFyezg37PLLJTdf1elLBEMmyJo7'}, 
										{'image_name': 'lp6.jpg', 'image_id': '1lOMBZfoY8xqPZdmAH1xhDcdvKKct-T3B'}, 
										{'image_name': 'lp7.jpg', 'image_id': '17aJI9Fi2yFhen1V8hZGl9FDZond8MJRg'}, 
										{'image_name': 'lp8.jpg', 'image_id': '1aLh5p7De2pGecAk1HIDXtKKbW-qi0a_r'}, 
										{'image_name': 'lp2.jpg', 'image_id': '1OoRBGrbylp7r_CbLoMdS1E0F97l5HIxs'}, 
										{'image_name': 'lp1.jpg', 'image_id': '15BxnQscoe2-2MmGsTRBqwATFyEtRffx6'}, 
										{'image_name': 'lp3.jpg', 'image_id': '1lirTf2_3evl7K91_MyuFKqBLAcddvGHY'}, 
										{'image_name': 'lp4.jpg', 'image_id': '1o8w3A0V1YLEJLOXQmTlb7aMpBTA5tnR8'}, 
										{'image_name': 'lp5.jpg', 'image_id': '1aW2IYO_4qlpbBw6ogVA1ZSry4zqHxe4l'}]}

{'folder_name': '[lung][benign][infection][spot_diagnosis][uncommon][pneumocystis_pneumonia]', 'google_drive_id': '1c0JS8viihak1X7DUrxB0Wf-vD-2mTYv1', 'organ': 'lung', 'disease_type': 'benign', 'subtype': 'infection', 'complexity': 'spot_diagnosis', 'incidence': 'uncommon', 'name': 'pneumocystis_pneumonia', 'printable_name': 'pneumocystis pneumonia', 'files_within_folder': [{'textfile_name': 'pneumocystis_pneumonia.txt', 'textfile_id': '1L2UrvzK7SNvCiZcHQX9CjoyicRx4qwSR'}, {'image_name': 'med_lp.jpg', 'image_id': '1zHwEcC_ReLg6g7ToCSh00t8Z0RqbRhTI'}]}

{'folder_name': '[thyroid][malignant][tumour][spot_diagnosis][common][papillary_thyroid_carcinoma]', 'google_drive_id': '1m1PUfDjppvv9fs1H9P6M4__qcY-s5vES', 'organ': 'thyroid', 'disease_type': 'malignant', 'subtype': 'tumour', 'complexity': 'spot_diagnosis', 'incidence': 'common', 'name': 'papillary_thyroid_carcinoma', 'printable_name': 'papillary thyroid carcinoma', 'files_within_folder': [{'textfile_name': 'papillary_thyroid_carcinoma.txt', 'textfile_id': '13ctbOpLgIpwP2fptZbcnVndGiH3cZtGP'}, {'image_name': 'po6.jpg', 'image_id': '10exI8OvtEd1Hbxs4IVlgIKo86md8na1h'}, {'image_name': 'po5.jpg', 'image_id': '1iHJcDI2VradG9IXiUkBzQOMPs0kPDP06'}, {'image_name': 'po4.jpg', 'image_id': '1oiSwgSYCVDqxvPSgizDgd8Vru330eMQc'}, {'image_name': 'po3.jpg', 'image_id': '1par8XUwzAoJCIfimVUZu0TZQ-9mXck5t'}, {'image_name': 'po2.jpg', 'image_id': '1xCSM4-ibbsO5c9kprxdbaiVTUfa9q3xd'}, {'image_name': 'po1.jpg', 'image_id': '1BKl21WWKspuDjDHC2ZlQtggoAa6V7PUI'}]}

'''