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

def list_files_raw_api(): # Not working yet

    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Test from https://developers.google.com/drive/api/v3/search-parameters
    page_token = None
    count=0
    while True:
        response = drive.files().list(fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()
        for file in response.get('files', []):
            count+=1
            # Process change
            print(f'Found file: %s (%s)' % (file.get('name'), file.get('id')))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    print(f'There were {count} files present in the second test')

def download_a_file(file_id = '1sS9ZDxt1sN-PKYhIdcSuLhBLERfx-JFk'):
    # Inspiration
    # https://stackoverflow.com/questions/50367862/how-to-access-google-drive-image-in-canvas

    # https://www.googleapis.com/drive/v3/files/fileId/export

    file = requests.get('https://www.googleapis.com/drive/v3/files/{file_id}')
    pprint.PrettyPrinter().pprint(file.content)   
    print('done here')   

if __name__ == '__main__':
    list_files_raw_api()
    '''
    with temporary_work_dir():
        download_a_file()
    '''