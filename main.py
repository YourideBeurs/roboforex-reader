import os.path
import base64
import re
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  label = 'INBOX'
  label = 'RoboForex'
#   query = f'in:{label}'
  query_from = 'ENTER YOUR EMAIL HERE'
  query_subject = 'Daily Confirmation'

  query = 'from: ' + query_from + ' subject:"' + query_subject + '"'

  # Initialize an empty list to store the combined results
  combined_results = []
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId='me', q=query).execute()
    # results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages',[])
    # results = service.users().labels().list(userId="me").execute()
    # labels = results.get("labels", [])

    if not messages:
      print('No new messages.')
    else:
      for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()                
        data = msg['payload']['parts'][0]['body']['data']
        byte_code = base64.urlsafe_b64decode(data)
        text = byte_code.decode("utf-8")

        match = re.search('\*ENTER YOUR NAME HERE\*\s+(.+),', text)
        date = match.group(1)
        date_format = "%Y %B %d"

        # print(date)
        date = datetime.datetime.strptime(date, date_format)
        # print(f"Parsed date: {parsed_date}")

        match = re.search('Balance: (.*)\s+Margin', text)
        balance = match.group(1)
        balance = balance.replace(' ', '')
        balance = float(balance)
        # print(balance)
        # double_value = float(balance)
        # print(f"Converted double value: {double_value}")

        # print(f"[{date}] {balance}")

        # Add the combined result to the list
        combined_results.append((date, balance))

        # print ("This is the message: "+ str(text))

        # email_body = msg['payload']['body']['data']  # Get the entire email body

        # # Decode the base64-encoded email body
        # decoded_body = base64.urlsafe_b64decode(email_body).decode('utf-8')

        # # Print the entire email text
        # print('Email Text:')
        # print(decoded_body)
        
        # email_data = msg['payload']['headers']
        # for values in email_data:
        #     name = values['name']
        #     if name == 'From':
        #         from_name= values['value']
        #         print('From: ' + from_name)           
                # for part in msg['payload']['parts']:
                #     try:
                #         data = part['body']["data"]
                #         byte_code = base64.urlsafe_b64decode(data)

                #         text = byte_code.decode("utf-8")
                #         print ("This is the message: "+ str(text))

                #         # mark the message as read (optional)
                #         msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()                                                       
                #     except BaseException as error:
                #         pass             
    # if not labels:
    #   print("No labels found.")
    #   return
    # print("Labels:")
    # for label in labels:
    #   print(label["name"])

    # Sort the combined results by date
    sorted_results = sorted(combined_results, key=lambda x: x[0])
    for date, balance in sorted_results:
        print(f"[{date}] {balance}")


  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()