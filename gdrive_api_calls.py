from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import random

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

# Auto-iterate through all files that matches this query
def list_all_files(folder):
	file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
	results = {}
	for file1 in file_list:
		#print('title: %s, id: %s' % (file1['title'], file1['id']))
		results[file1['title']] = file1['id']
	print(results)
	return results

def get_file_ids_from_folder(folder_id):
	# Returns an array of ids for the images within a given folder
	image_ids = []
	image_extensions = ['.jpeg', '.jpg', '.bmp', '.tif', '.png', '.gif']

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

	# pick random id
	random_id = random.choice(image_id_list)
	# create pydrive object
	image = drive.CreateFile({'id':random_id})
	# download image
	image.GetContentFile(f'static/temporary_image_with_id_{image_id}')
	# record the location/name
	file_location=f'static/temporary_image_with_id_{image_id}'
	
	return file_location


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

# list_all_files('dummy_folder')