import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# Define scopes - Added Cloud Billing and Cloud Platform for full management
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/admin.directory.user',
    'https://www.googleapis.com/auth/admin.directory.group',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/cloud-billing',
    'https://www.googleapis.com/auth/cloud-platform'
]

def generate_token():
    creds = None
    token_path = 'config/google_token.json'
    credentials_path = 'config/credentials.json'

    # Ensure config directory exists
    if not os.path.exists('config'):
        os.makedirs('config')

    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            print('Token invalid or scopes changed, regenerating...')
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                print('Token refresh failed, regenerating...')
                creds = None

        if not creds:
            if not os.path.exists(credentials_path):
                print(f'Error: {credentials_path} not found.')
                print('Please download your OAuth 2.0 Client Secret JSON from Google Cloud Console')
                print('and save it as config/credentials.json')
                return

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            print(f'✅ Token saved to {token_path}')

if __name__ == '__main__':
    generate_token()
