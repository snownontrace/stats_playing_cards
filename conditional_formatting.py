import os, argparse, pickle
import numpy as np
from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def highlight_game_id(game_id, service, spreadsheet_id, sheet_id):
    '''
    game_id: integer of game_id to highlight
    service: Google sheets API service (built by "discovery")
    
    
    '''
    batch_update_spreadsheet_request_body = {
      "requests": [
        {
          "addConditionalFormatRule": {
            "rule": {
              "ranges": [
                {
                  "sheetId": sheet_id,
                  "startColumnIndex": 0, # 0-based, included
                  "endColumnIndex": 1, # 0-based, not included
                },
              ],
              "booleanRule": {
                "condition": {
                  "type": "NUMBER_EQ",
                  "values": [
                    {
                      "userEnteredValue": str(game_id)
                    }
                  ]
                },
                "format": {
                  'backgroundColor': {'blue': 0.8039216,
                                      'green': 0.88235295,
                                      'red': 0.7176471},
                }
              }
            },
            "index": 0
          },
        }
      ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()
    
    
    batch_update_spreadsheet_request_body = {
      "requests": [
        {
          "addConditionalFormatRule": {
            "rule": {
              "ranges": [
                {
                  "sheetId": sheet_id,
                  "startColumnIndex": 0, # 0-based, included
                  "endColumnIndex": 1, # 0-based, not included
                },
              ],
              "booleanRule": {
                "condition": {
                  "type": "NUMBER_NOT_EQ",
#                   "type": "NUMBER_EQ",
                  "values": [
                    {
                      "userEnteredValue": str(game_id)
                    }
                  ]
                },
                "format": {
                  'backgroundColor': {'blue': 1,
                                      'green': 1,
                                      'red': 1},
                }
              }
            },
            "index": 1
          },
        }
      ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()
    
    return response


def highlight_win(service, spreadsheet_id, sheet_id,
                  col_start, col_end, row_start, row_end):
    '''
    '''
    batch_update_spreadsheet_request_body = {
      "requests": [
        {
          "addConditionalFormatRule": {
            "rule": {
              "ranges": [
                {
                  "sheetId": sheet_id,
                  "startColumnIndex": col_start-1, # 0-based, included
                  "endColumnIndex": col_end, # 0-based, not included
                  "startRowIndex": row_start-1, # 0-based, included
                  "endRowIndex": row_end, # 0-based, not included
                },
              ],
              "booleanRule": {
                "condition": {
                  "type": "TEXT_EQ",
                  "values": [
                    {
                      "userEnteredValue": 'win',
                    }
                  ]
                },
                "format": {
                    "textFormat": {
                        'foregroundColor': {'blue': 0.3254902,
                                            'green': 0.65882355,
                                            'red': 0.20392157},
                    },
                    'backgroundColor': {'blue': 0.8039216,
                                        'green': 0.88235295,
                                        'red': 0.7176471},
                },
              },
            },
            "index": 0
          },
        }
      ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()
    
    return response

    
def highlight_Yes(service, spreadsheet_id, sheet_id,
                  col_start, col_end, row_start, row_end):
    '''
    '''
    batch_update_spreadsheet_request_body = {
      "requests": [
        {
          "addConditionalFormatRule": {
            "rule": {
              "ranges": [
                {
                  "sheetId": sheet_id,
                  "startColumnIndex": col_start-1, # 0-based, included
                  "endColumnIndex": col_end, # 0-based, not included
                  "startRowIndex": row_start-1, # 0-based, included
                  "endRowIndex": row_end, # 0-based, not included
                },
              ],
              "booleanRule": {
                "condition": {
                  "type": "TEXT_EQ",
                  "values": [
                    {
                      "userEnteredValue": 'Yes',
                    }
                  ]
                },
                "format": {
#                     "textFormat": {
#                         'foregroundColor': {'blue': 0.3254902,
#                                             'green': 0.65882355,
#                                             'red': 0.20392157},
#                     },
                    'backgroundColor': {'blue': 0.8039216,
                                        'green': 0.88235295,
                                        'red': 0.7176471},
                },
              },
            },
            "index": 0
          },
        }
      ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()
    
    return response


def highlight_lose(service, spreadsheet_id, sheet_id,
                   col_start, col_end, row_start, row_end):
    '''
    '''
    
    batch_update_spreadsheet_request_body = {
      "requests": [
        {
          "addConditionalFormatRule": {
            "rule": {
              "ranges": [
                {
                  "sheetId": sheet_id,
                  "startColumnIndex": col_start-1, # 0-based, included
                  "endColumnIndex": col_end, # 0-based, not included
                  "startRowIndex": row_start-1, # 0-based, included
                  "endRowIndex": row_end, # 0-based, not included
                },
              ],
              "booleanRule": {
                "condition": {
                  "type": "TEXT_EQ",
                  "values": [
                    {
                      "userEnteredValue": 'lose',
                    }
                  ]
                },
                "format": {
                    "textFormat": {
                        'foregroundColor': {'blue': 0.627451,
                                            'green': 0.48235294,
                                            'red': 0.7607843},
                    },
                    'backgroundColor': {'blue': 0.8627451,
                                        'green': 0.81960785,
                                        'red': 0.91764706},
                },
              }
            },
            "index": 0
          },
        }
      ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()
    
    return response


def highlight_No(service, spreadsheet_id, sheet_id,
                 col_start, col_end, row_start, row_end):
    '''
    '''
    
    batch_update_spreadsheet_request_body = {
      "requests": [
        {
          "addConditionalFormatRule": {
            "rule": {
              "ranges": [
                {
                  "sheetId": sheet_id,
                  "startColumnIndex": col_start-1, # 0-based, included
                  "endColumnIndex": col_end, # 0-based, not included
                  "startRowIndex": row_start-1, # 0-based, included
                  "endRowIndex": row_end, # 0-based, not included
                },
              ],
              "booleanRule": {
                "condition": {
                  "type": "TEXT_EQ",
                  "values": [
                    {
                      "userEnteredValue": 'No',
                    }
                  ]
                },
                "format": {
#                     "textFormat": {
#                         'foregroundColor': {'blue': 0.627451,
#                                             'green': 0.48235294,
#                                             'red': 0.7607843},
#                     },
                    'backgroundColor': {'blue': 0.8627451,
                                        'green': 0.81960785,
                                        'red': 0.91764706},
                },
              }
            },
            "index": 0
          },
        }
      ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id,
                                                 body=batch_update_spreadsheet_request_body)
    response = request.execute()
    
    return response