import os, argparse
# import re, pickle
import pandas as pd
from get_game_info import get_df_game_record, get_game_info
from write_google_sheet import write_google_sheet
# from googleapiclient import discovery
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

def get_index(s):
    '''
    Convert a string of letter notation to number index.
    e.g. 'A' -> 1, 'Z' -> 26, 'AA' -> 27, 'AZ' -> 52
    
    '''
    idx = 0
    for i in range(len(s)):
        temp = ord( s[-(i+1)].lower() ) - 96
        idx += temp * ( 26**i )
        
    return idx


def add_game_record(game_info_file,
                    update_local=True, update_remote=True,
                    csv_log=None, spreadsheet_id=None, range_=None):
    '''
    '''
    
    # provide default values for optional parameters
    if csv_log is None:
        csv_log = './log/game_record.csv'
        
    if spreadsheet_id is None:
        # This is the Google spreadsheet hosting the game record
        spreadsheet_id = '1So3PBr9gV3I0LzApZOgJlQew2QjM1wAiWhR50rAnHRg'
        
    if range_ is None:
        # This is the first sheet of the spreadsheet
        range_ = 'Sheet1'
        
    # read in game record history from local record if exists;
    # otherwise, pull data from Google spreadsheet
    game_record_df = get_df_game_record(force_remote=False,
                                        csv_log=csv_log,
                                        spreadsheet_id=spreadsheet_id,
                                        range_name=range_)
    
    # obtain current game info from the game info text file
    game_info_dict = get_game_info(game_info_file, game_record_df)
    
    if update_remote:
        # reformat dict to 2D array for writing to Google spreadsheet
        data_in_columns = [game_info_dict[key] for key in game_info_dict.keys()]
        write_response = write_google_sheet(data_in_columns, spreadsheet_id, range_)
        
    if update_local:
        # reformat dict to pandas data frame
        game_info_df = pd.DataFrame(game_info_dict)
        new_record_df = pd.concat([game_record_df, game_info_df], axis=0)
        new_record_df.reset_index(drop=True, inplace=True)
        new_record_df.to_csv(csv_log, index=False)
        
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("game_info_file", nargs='?',
                        help="optional; path to txt file of current game info.",
                        default='current_game.txt')
    args = parser.parse_args()
    
    add_game_record(args.game_info_file)