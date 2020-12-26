import os, argparse, pickle
import numpy as np
from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def write_google_sheet(data_in_columns,
                       spreadsheet_id=None, range_=None):
    '''
    Write data to a Google spreadsheet using the given spreadsheet_id and range_


    Parameters
    ----------
    
    data_in_columns:
        The data to write. Has to be a 2D array or alike.
        
    spreadsheet_id:
        The identifier of a spreadsheet, which is embedded in the Google Spreadsheet URL.
        For example:
            https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}

    range_:
        Specify the range of data. For example: 'Sheet1!A1:E5'


    Outputs
    -------

    1. The values stored in data_in_columns are written to the Google spreadsheet
    2. A message printed out to show the number of updated rows and columns
    
    
    Returns
    -------
    
    The response dictionary.
    
        
    '''
    
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

    # How the input data should be interpreted.
    value_input_option = 'RAW'

    # How the input data should be inserted.
    insert_data_option = 'INSERT_ROWS'

    value_range_body = {
        # Add desired entries to the request body.
        'range': range_,
        'majorDimension': 'COLUMNS',
        "values": data_in_columns
    }

    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option,
                                                     body=value_range_body)
    response = request.execute()

    print('Successfully updated', response['updates']['updatedRows'], 'rows and', 
          response['updates']['updatedColumns'], 'columns of data in', response['tableRange'])

    return response

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("spreadsheet_id", nargs='?',
                        help="In spreadsheet URL: \"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}\"")
    parser.add_argument("range_name", nargs='?',
                        help="optional; the data range to obtain; example: \'Sheet1!A1:E5\'",
                        default='Sheet1')
    args = parser.parse_args()
    
    # Generate testing data
    data_ = np.random.rand(5, 10)
    data_in_columns = [list(i) for i in list(data_)]
    print('Writing 5x10 random numbers to Google spreadsheet...')
    write_google_sheet(data_in_columns, args.spreadsheet_id, args.range_name)
