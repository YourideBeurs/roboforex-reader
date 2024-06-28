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
    messages = results.get('messages',[])

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

        match = re.search(r'Balance: (.*)\s+Margin', text)
        balance = match.group(1)
        balance = balance.replace(' ', '')
        balance = float(balance)

        combined_results.append((date, balance))

    # Sort the combined results by date
    sorted_results = sorted(combined_results, key=lambda x: x[0])
    for date, balance in sorted_results:
        print(f"[{date}] {balance}")


  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()