import argparse
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def get_sheet_data(spreadsheet_id, range_name):
    """
    Get the data from Google spreadsheet using the given spreadsheet_id and range_name

    Parameters
    ----------

    spreadsheet_id:
        The identifier of a spreadsheet, which is embedded in the Google Spreadsheet URL.
        For example:
            https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}

    range_name:
        Specify the range of data to obtain.

    Returns
    -------

    data:
        A list of values corresponding to rows of the specified range in the spreadsheet
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()
    data = result.get('values', [])

    if not data:
        print('No data found.')
    else:
        print("COMPLETE: Data copied")

    return data

def main(spreadsheet_id, range_name):
    """
    Get the data from Google spreadsheet using the given spreadsheet_id and range_name

    Parameters
    ----------

    spreadsheet_id:
        The identifier of a spreadsheet, which is embedded in the Google Spreadsheet URL.
        For example:
            https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}

    range_name:
        Specify the range of data to obtain.

    Returns
    -------

    data:
        A list of values corresponding to rows of the specified range in the spreadsheet
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=range_name).execute()
    data = result.get('values', [])

    if not data:
        print('No data found.')
    else:
        # print("COMPLETE: Data copied")
        for row in data:
            print(','.join(row))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("spreadsheet_id",
                        help="the string between \"https://docs.google.com/spreadsheets/d/\" and \"/edit#gid={sheet_id}\" of the spreadsheet URL")
    parser.add_argument("range_name", nargs='?',
                        help="optional; the data range to obtain; example: \'Sheet1!A1:E5\'",
                        default='Sheet1')
    args = parser.parse_args()
    main(args.spreadsheet_id, args.range_name)
