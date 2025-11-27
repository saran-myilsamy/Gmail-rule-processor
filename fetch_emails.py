import base64
from email.utils import parsedate_to_datetime
from gmail_authenticator import GmailAuthenticator
from database_manager import DatabaseManager
import config

class EmailFetcher:
    def __init__(self, service, db_manager):
        self.service = service
        self.db = db_manager
        
    def parse_email_headers(self, headers):
        header_dict = {}
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            header_dict[name] = value
        return header_dict
    
    def get_email_body(self, payload):
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8', errors='ignore')
                        break
                elif 'parts' in part:
                    body = self.get_email_body(part)
                    if body:
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(
                payload['body']['data']).decode('utf-8', errors='ignore')
        
        return body
    
    def fetch_emails(self, max_results=100):
        print(f"Fetching up to {max_results} emails...")
        
        try:
            results = self.service.users().messages().list(
                userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            if not messages:
                print('No messages found.')
                return
            
            print(f'Found {len(messages)} messages. Processing...')
            
            for idx, message in enumerate(messages, 1):
                try:
                    msg = self.service.users().messages().get(
                        userId='me', id=message['id'], format='full').execute()
                    
                    headers = self.parse_email_headers(
                        msg['payload'].get('headers', []))
                    
                    from_email = headers.get('from', '')
                    to_email = headers.get('to', '')
                    subject = headers.get('subject', '')
                    date_str = headers.get('date', '')
                    
                    received_date = None
                    if date_str:
                        try:
                            received_date = parsedate_to_datetime(date_str)
                        except:
                            received_date = None
                    
                    body = self.get_email_body(msg['payload'])
                    
                    is_read = 'UNREAD' not in msg.get('labelIds', [])
                    labels = msg.get('labelIds', [])
                    
                    email_data = {
                        'message_id': msg['id'],
                        'thread_id': msg.get('threadId', ''),
                        'from_email': from_email,
                        'to_email': to_email,
                        'subject': subject,
                        'message_body': body[:5000],  # limit body size
                        'received_date': received_date,
                        'is_read': is_read,
                        'labels': labels
                    }
                    
                    self.db.insert_email(email_data)
                    
                    if idx % 10 == 0:
                        print(f'Processed {idx}/{len(messages)} emails...')
                        
                except Exception as e:
                    print(f"Error processing message {message['id']}: {e}")
                    continue
            
            print(f'Successfully processed {len(messages)} emails')
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            raise

def main():
    authenticator = GmailAuthenticator()
    service = authenticator.get_service()
    
    db = DatabaseManager(config.DB_CONFIG)
    db.connect()
    db.create_tables()
    
    fetcher = EmailFetcher(service, db)
    fetcher.fetch_emails(max_results=50)
    
    db.close()
    print("Email fetch complete!")

if __name__ == '__main__':
    main()