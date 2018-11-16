# Tutorial https://codelabs.developers.google.com/codelabs/gsuite-apis-intro/#0

from google.oauth2 import service_account
import googleapiclient.discovery
import os, tempfile, zipfile, pprint
from contextlib import contextmanager
import requests

from pydrive.auth import GoogleAuth, ServiceAccountCredentials
from pydrive.drive import GoogleDrive

SERVICE_ACCOUNT_FILE = 'service_account_credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'
CREDENTIALS_LOCATION = 'service_account_credentials.json'

@contextmanager
def temporary_work_dir():
    # Inspiration to download images to temp file in AWS lambda
    # https://stackoverflow.com/questions/48364250/write-to-tmp-directory-in-aws-lambda-with-python
    old_work_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        print(os.getcwd())
        try:
            yield
        finally:
            os.chdir(old_work_dir)

def list_files_raw_api(): # Not workin yet

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Call the Drive v3 API
    # https://developers.google.com/drive/api/v3/reference/files/list
    results = drive.files().list().execute()
    print('the results',results)
    items = results.get('files', [])

    print(items)
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print(item)

def list_files_pydrive(file_id = '1NmyzauLOKFygiSfFySgkVX8h7XXFt5oz'):
    # As per https://github.com/gsuitedevs/PyDrive/issues/107
    gauth = GoogleAuth()
    gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_LOCATION, SCOPES)
    drive = GoogleDrive(gauth)
    
    # Create pydrive object
    file_id = str(file_id)
    my_file = drive.CreateFile({'id': file_id}) 
    # Download the file
    my_file.GetContentFile('freshly_downloaded_image.jpg')

  


def download_a_file(file_id = '1NmyzauLOKFygiSfFySgkVX8h7XXFt5oz'):
    # Inspiration
    # https://stackoverflow.com/questions/50367862/how-to-access-google-drive-image-in-canvas

    # https://www.googleapis.com/drive/v3/files/fileId/export

    file = requests.get('https://www.googleapis.com/drive/v3/files/{file_id}')
    pprint.PrettyPrinter().pprint(file.content)   
    print('done here')   

if __name__ == '__main__':
    list_files_pydrive()
    '''
    with temporary_work_dir():
        download_a_file()
    '''