import os.path
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GmailClient:
    def __init__(self, credentials_path='config/secure/credentials.json', token_path='config/secure/token.json', scopes=None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes or ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
        self.service = self.get_gmail_service()

    def get_gmail_service(self):
        """If the gmail api credentials are provided, returns a Gmail service object, otherwise returns None."""
        try:
            creds = None
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                    creds = flow.run_local_server(port=0)
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            return build('gmail', 'v1', credentials=creds)
        except Exception:
            return None

    def create_message(self, sender, to, subject, message_text):
        """Create a message for an email."""
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def send_email(self, to, subject, body):
        """Send an email message."""
        try:
            message = self.create_message('me', to, subject, body)
            sent = self.service.users().messages().send(userId='me', body=message).execute()
            print(f"Message Id: {sent['id']}")
        except HttpError as error:
            print(f'An error occurred: {error}')

    def read_emails(self, label_ids=['INBOX'], max_results=5):
        """Returns a list of emails from the user's mailbox."""
        try:
            results = self.service.users().messages().list(userId='me', labelIds=label_ids, maxResults=max_results).execute()
            messages = results.get('messages', [])

            if not messages:
                print("No messages found.")
                return []

            emails = []
            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()

                email_data = {
                    'subject': None,
                    'sender': None,
                    'content': None
                }

                headers = msg.get('payload', {}).get('headers', [])
                for header in headers:
                    if header['name'].lower() == 'subject':
                        email_data['subject'] = header['value']
                    elif header['name'].lower() == 'from':
                        email_data['sender'] = header['value']

                parts = msg.get('payload', {}).get('parts', [])
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            email_data['content'] = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
                            break

                emails.append(email_data)

            return emails

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
