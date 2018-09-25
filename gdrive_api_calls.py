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
	# TODO

	pass

list_all_files('dummy_folder')