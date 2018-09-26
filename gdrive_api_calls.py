from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

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

def get_photo(filename,id):
	# Returns an array of image names of downloaded images (temporary)
	# Format ['static/image_index','static/image_index']

	# Create a pydrive object for the folder
	folder = drive.CreateFile({'id':id})
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

def clear_static_folder(filename):
	# TODO Once an image has been used, remove from static filder.
	pass

# list_all_files('dummy_folder')