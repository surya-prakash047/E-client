from .oauth import create_service
import base64
from bs4 import BeautifulSoup


class gmailApi:

    def __init__(self):
        self.CRED_FILE = 'config/client_secret.json'
        self.API_SERVICE_NAME = 'gmail'
        self.API_VERSION = 'v1'
        self.SCOPES = ['https://mail.google.com/']

        # Create gmail service instance 
        self.service = create_service(self.CRED_FILE,self.API_SERVICE_NAME,self.API_VERSION,self.SCOPES)
    def mark_as_read(self, email_id):
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking email as read: {e}")
            return False

    def mark_as_unread(self, email_id):
        try:
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error marking email as unread: {e}")
            return False

    def fetch_emails(self,count=10):
        try:
            results = self.service.users().messages().list(userId='me',labelIds=['INBOX'],maxResults=count).execute()
            messages = results.get('messages',[])

            if not messages: # if no messages found
                print('No messages found')
                return []
            
            print(f'{len(messages)} message(s) found')
            

            emails = []
            for msg in messages:
                message = self.service.users().messages().get(userId='me',id=msg['id']).execute() # fetch the message using service

                # Extract the headers from the message and storing it as a dict
                headers = {}
                for header in message['payload']['headers']:
                    headers[header['name']] = header['value']

                # Extract the email data from the message and storing it as a dict
                # Extracting body data
                body = self.extract_body_content(message)
                
                # Check for attachments
                has_attachment = False
                attachment_types = []
                
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if 'filename' in part and part['filename']:
                            has_attachment = True
                            if 'mimeType' in part:
                                attachment_types.append(part['mimeType'])

                email_data = {
                    'id':msg['id'],
                    'subject':headers.get('Subject','No Subject'),
                    'snippet':message.get('snippet',''),
                    'from': headers.get('From','No Sender'),
                    'to': headers.get('To','No Receipient'),
                    'date': headers.get('Date','No Date'),
                    'labels': message.get('labelIds',[]),
                    'body': body,
                    'has_attachment': has_attachment,
                    'attachment_types': attachment_types,
                    'is_read': 'UNREAD' not in message.get('labelIds', [])
                }
                emails.append(email_data)
            return emails
        except Exception as e:
            print(e)
            return []
    def decode_and_clean(self, data):
        try:
            decoded_bytes = base64.urlsafe_b64decode(data)
            text = decoded_bytes.decode('utf-8')
            
            if '<html' in text.lower() or '<div' in text.lower():
                soup = BeautifulSoup(text, 'html.parser')
                return soup.get_text(separator='\n', strip=True)
            return text
        except:
            return ''
    def extract_body_content(self, message):
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] in ['text/plain', 'text/html']:
                    data = part['body'].get('data', '')
                    if data:
                        return self.decode_and_clean(data)
        
        if 'body' in message['payload']:
            data = message['payload']['body'].get('data', '')
            if data:
                return self.decode_and_clean(data)
                
        return ''
    def move_message(self, email_id, folder_name):
        try:
            # Get all labels
            labels = self.service.users().labels().list(userId='me').execute()
            
            # Find or create the destination folder/label
            label_id = None
            for label in labels.get('labels', []):
                if label['name'].lower() == folder_name.lower():
                    label_id = label['id']
                    break
            
            # If label doesn't exist, create it
            if not label_id:
                label = self.service.users().labels().create(
                    userId='me',
                    body={'name': folder_name}
                ).execute()
                label_id = label['id']
            
            # Move message by adding new label and removing from inbox
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={
                    'addLabelIds': [label_id],
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            return True
            
        except Exception as e:
            print(f"Error moving message: {e}")
            return False

           