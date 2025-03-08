import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Import Necessary Libraries

def create_service(client_secret_file,api_name,api_version,*scopes,prefix=''):
    # make the passing values constants
    CLIENT_SECRET_FILE = client_secret_file # directory of the client secret file
    API_SERVICE_NAME = api_name # name of the service we want to use
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]] 

    # token file validation

    creds = None # credentials in token file
    
    working_dir = os.getcwd() # get the current directory
    token_dir = 'token_files'
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json' # name of the token file

    # check if the token directory exists or else create directory
    if not os.path.exists(os.path.join(working_dir,token_dir)):
        os.mkdir(os.path.join(working_dir,token_dir))
    
    if os.path.exists(os.path.join(working_dir,token_dir,token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir,token_dir,token_file),SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else :
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE,SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir,token_dir,token_file),'w') as token:
            token.write(creds.to_json())
        
    try:
        service = build(API_SERVICE_NAME,API_VERSION,credentials=creds,static_discovery=False)
        #print(API_SERVICE_NAME,API_VERSION,'service created successfully')
        return service
        
    except Exception as e :
        print(e)
        print(f'failed to started create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir,token_dir,token_file))
        return None
    




