import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import config

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_youtube():
    if config.DRY_RUN and not os.path.exists(config.TOKEN_FILE):
        return None
        
    creds = None
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        if not config.DRY_RUN:
            with open(config.TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
                
    return build('youtube', 'v3', credentials=creds)