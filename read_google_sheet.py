import os, argparse, pickle
from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def read_google_sheet(spreadsheet_id=None, range_=None):
    """
    Get the data from Google spreadsheet using the given spreadsheet_id and range_

    Parameters
    ----------

    spreadsheet_id:
        The identifier of a spreadsheet, which is embedded in the Google Spreadsheet URL.
        For example:
            https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}

    range_:
        Specify the range of data to obtain.

    Returns
    -------

    data:
        A list of values corresponding to rows of the specified range in the spreadsheet
    """
    # Provide default values for optional parameters
    if spreadsheet_id is None:
        # Spreadsheet for testing
        spreadsheet_id = '1DkYahCdFH2EUNKBJJ-6zt55bdj4xgLeKZ-9visw6GrQ'
        
    if range_ is None:
        # Default first sheet name
        range_ = 'Sheet1'
        
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
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

    service = discovery.build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                 range=range_).execute()
    rows = result.get('values', [])
    
    print('{0} rows retrieved.'.format(len(rows)))
    
#     request = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
#                                                   range=range_)
#     response = request.execute()
#     data = response.get('values', [])

#     if not data:
#         print('No data found in the Google spreadsheet.')
#     else:
#         print("Successfully copied data from Google spreadsheet.")

    return rows

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('spreadsheet_id', nargs='?',
                        help='the string between \"https://docs.google.com/spreadsheets/d/\" and \"/edit#gid={sheet_id}\" of the spreadsheet URL')
    parser.add_argument('range_', nargs='?',
                        help='optional; the data range to obtain; example: \'Sheet1!A1:E5\'',
                        default='Sheet1')
    args = parser.parse_args()
    
    print('Reading data from Google spreadsheet...')
    data = read_google_sheet(args.spreadsheet_id, args.range_)
    
    print('Printing first 5 rows of data:')
    n_rows = [5 if len(data)>5 else len(data)]
    for row in data[:n_rows[0]]:
        print(', '.join(row))