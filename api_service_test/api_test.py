# Tutorial https://codelabs.developers.google.com/codelabs/gsuite-apis-intro/#0

from google.oauth2 import service_account
import googleapiclient.discovery
import os, tempfile, zipfile, pprint, io 
import toml
from contextlib import contextmanager
import requests
from googleapiclient.http import MediaIoBaseDownload



SERVICE_ACCOUNT_FILE = 'service_account_credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'

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
            if count == 620:
                pprint.PrettyPrinter().pprint(file)  
            # Process change
            print(f'Found file: %s (%s)' % (file.get('name'), file.get('id')))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    print(f'There were {count} files found using the V3 service account API')

def list_disease_folders():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Test from https://developers.google.com/drive/api/v3/search-parameters
    page_token = None
    count=0
    while True:
        response = drive.files().list(q="mimeType = 'application/vnd.google-apps.folder'",
                                            fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()
        for file in response.get('files', []):
            count+=1
            # Process change
            print(f'Found file: %s (%s)' % (file.get('name'), file.get('id')))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    print(f'There were {count} folders found using the V3 service account API')

def list_folder_contents(folder_id=''):
    # Lists the file contents for a given folder 
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # Test from https://developers.google.com/drive/api/v3/search-parameters
    page_token = None
    count=0
    query = f"'{str(folder_id)}' in parents"
    while True:
        response = drive.files().list(q=query,
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            count+=1
            # Process change
            print(f'Found file: %s (%s)' % (file.get('name'), file.get('id')))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    print(f'There were {count} folders found using the V3 service account API')

def download_a_file(file_id = ''):
    # https://developers.google.com/drive/api/v3/manage-downloads
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


    request = drive.files().get_media(fileId=file_id)
    with temporary_work_dir():
        # This causes files to be saved in:
        # /private/var/folders/4n/31wr80mj5_g23g8kt79nz9zm0000gn/T/tmp9e8phnks
        fh = io.FileIO('newfangled_file.txt','wb') # changed from io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

        print('I am in',os.getcwd())
        for file in os.listdir('.'):
            print('I found: ',file)

        things = toml.load('newfangled_file.txt')
        pprint.PrettyPrinter().pprint(things) 

    print('now we are in ',os.getcwd())


    with temporary_work_dir():
        # This causes files to be saved in:
        # /private/var/folders/4n/31wr80mj5_g23g8kt79nz9zm0000gn/T/tmp9e8phnks
        fh = io.FileIO('newfangled_file.txt','wb') # changed from io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

        print('I am in',os.getcwd())
        for file in os.listdir('.'):
            print('I found: ',file)

        things = toml.load('newfangled_file.txt')
        pprint.PrettyPrinter().pprint(things) 

if __name__ == '__main__':
    
    download_a_file(file_id='12dO-Pv4InZuBOxwzCjbdWEct6Qw0-fVu')
    #list_folder_contents(folder_id='1EHnywbGUb21XHMC2qUGOppY1egbBLlRO')
    #list_disease_folders()
    #list_files_raw_api()
    '''
    with temporary_work_dir():
        download_a_file()
    '''