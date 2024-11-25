from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import os
import yaml
from pathlib import Path

class GmailAuthenticator:
    def __init__(self, config_path: str = 'configs/config.yaml'):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.SCOPES = self.config['auth']['scopes']
        self.credentials_path = self.config['auth']['credentials_path']
        self.token_path = self.config['auth']['token_path']
        self.redirect_uri = self.config['auth']['oauth']['redirect_uri']
        self.server_config = self.config['auth']['oauth']['server']
        self.success_message = self.config['auth']['oauth']['success_message']
        self.creds = None

        # Create necessary directories
        Path(os.path.dirname(self.credentials_path)).mkdir(exist_ok=True)
        Path(os.path.dirname(self.token_path)).mkdir(exist_ok=True)

    def authenticate(self):
        """Handles the Gmail OAuth2 authentication flow."""
        if os.path.exists(self.token_path):
            print("Loading existing credentials...")
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Refreshing expired credentials...")
                self.creds.refresh(Request())
            else:
                print("Starting new authentication flow...")
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}. "
                        "Please download it from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.SCOPES,
                    redirect_uri=self.redirect_uri
                )

                # Run the local server to handle the redirect
                print(f"\nStarting local server on {self.server_config['host']}:{self.server_config['port']}")
                self.creds = flow.run_local_server(
                    host=self.server_config['host'],
                    port=self.server_config['port'],
                    success_message=self.success_message,
                    authorization_prompt_message="Please authorize the application.",
                    redirect_uri_trailing_slash=False
                )

                # Save the credentials for future use
                print("Saving credentials for future use...")
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)

        return build('gmail', 'v1', credentials=self.creds)