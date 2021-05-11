from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    global msg
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
       
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

  
    results = service.users().messages().list(userId='me',labelIds=['INBOX'],q="is:unread").execute()
    labels = results.get('messages', [])

    if not labels:
        return str("0")
    else:
        print('messages:')
        message_cnt = 0
        for message in labels:
            msg = service.users().messages().get(userId='me',id=message['id']).execute()
            message_cnt+=1
        print(message_cnt)

if __name__ == '__main__':
    main()