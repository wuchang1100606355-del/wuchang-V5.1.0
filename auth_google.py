
import os
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Configuration
SCOPES = ['https://www.googleapis.com/auth/tasks']
BASE_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = BASE_DIR / "config" / "google_credentials.json"
TOKEN_PATH = BASE_DIR / "config" / "google_token.json"

def main():
    credentials_path = CREDENTIALS_PATH
    print(f"Checking credentials at: {credentials_path}")
    
    if not credentials_path.exists():
        # Fallback to other locations if not in config
        potential_paths = [
            BASE_DIR / "google_credentials.json",
            BASE_DIR / "scripts" / "google_credentials.json"
        ]
        for p in potential_paths:
            if p.exists():
                print(f"Found credentials at: {p}")
                credentials_path = p
                break
        else:
            print("Error: google_credentials.json not found!")
            sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path), SCOPES
    )

    print("Starting local server for authentication...")
    print("Please open the following URL in the preview window (or your browser) to authorize:")
    
    # run_local_server will print the URL to stdout if open_browser is False
    # We set port=0 to let the OS choose a free port to avoid permission errors
    # hd='wuchang.life' restricts sign-in to the specific domain
    try:
        print("Starting OAuth flow...")
        creds = flow.run_local_server(
            port=0, 
            open_browser=False, 
            prompt='consent', 
            hd='wuchang.life',
            authorization_prompt_message='Please visit this URL: {url}',
            success_message='Authentication successful! You can close this window.',
            timeout_seconds=300  # 5 minutes timeout
        )
    except OSError as e:
        print(f"Error starting server: {e}")
        print("Trying fallback port 8088...")
        creds = flow.run_local_server(
            port=8088, 
            open_browser=False, 
            prompt='consent', 
            hd='wuchang.life',
            timeout_seconds=300
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save the credentials for the next run
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())
    
    print(f"\nAuthentication successful! Token saved to: {TOKEN_PATH}")

if __name__ == "__main__":
    main()
