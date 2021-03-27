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

def get_updated_range_idx(response):
    '''
    Previous efforts trying to update formatting of the spreadsheet.
    Note used yet.
    '''
    import re

    updatedRange = response['updates']['updatedRange']

    upper_left = updatedRange.split('!')[1].split(':')[0]
    lower_right = updatedRange.split('!')[1].split(':')[1]

    col_start = get_index(re.findall(r'[A-Z]+', upper_left)[0]) # 1-based, included
    col_end = get_index(re.findall(r'[A-Z]+', lower_right)[0]) # 1-based, included
    row_start = int(re.findall(r'[0-9]+', upper_left)[0]) # 1-based, included
    row_end = int(re.findall(r'[0-9]+', lower_right)[0]) # 1-based, included

    return [col_start, col_end, row_start, row_end]

def next_dealer_info(game_info_dict):
    '''
    Report the next dealer information and level to play
    '''
    current_dealer_index = game_info_dict['is_dealer'].index('Yes')
    n = len(game_info_dict['is_dealer'])
    for i in range(current_dealer_index+1,
                   current_dealer_index+len(game_info_dict['is_dealer'])):
        if game_info_dict['dealer_win_lose'][0] == 'win':
            if game_info_dict['on_dealer_team'][i%n] == 'Yes':
                print('Congrats to the dealer team!')
                print('##############################')
                next_dealer = game_info_dict['player_id'][i%n]
                print('Next dealer is:', next_dealer.replace('_', ' '))
                print('We are playing:', game_info_dict['level_after'][i%n],
                      'of round', game_info_dict['level_rounds_after'][i%n])
                print('##############################')
                break
            else:
                continue
        else:
            if game_info_dict['on_dealer_team'][i%n] == 'No':
                print('Congrats to the non_dealer team!')
                next_dealer = game_info_dict['player_id'][i%n]
                print('Next dealer is:', next_dealer.replace('_', ' '))
                print('We are playing:', game_info_dict['level_after'][i%n],
                      'of round', game_info_dict['level_rounds_after'][i%n])
                break
            else:
                continue

def add_game_record(game_info_file, force_remote,
                    update_local=True, update_remote=True,
                    csv_log=None, spreadsheet_id=None, range_=None):
    '''
    Read in current game info and update both local and remote record spreadsheets

    Input
    -----
    game_info_file:
        A text file storing current game info

    force_remote:
        Boolean value indicating whether data should be pulled from
        Google spreadsheet even when a local record is present

    update_local:
        Boolean value indicating whether to update the local record
        Default: True

    update_remote:
        Boolean value indicating whether to update the remote record
        Default: True

    csv_log:
        Path to the local record csv file
        If not provided, will use './log/game_record.csv'

    spreadsheet_id:
        The identifier of a spreadsheet, which is embedded in the Google Spreadsheet URL.
        For example:
            https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}
        If not provided, the id of the current game record spreadsheet will be used.

    range_:
        Specify the range of data. For example: 'Sheet1!A1:E5'
        If not provided, 'Sheet1' will be used.


    Output
    ------
        1. Text output of the next game information (who is the next dealer and what level to play).
        2. A copy of the game_info_file renamed as "game_log_{game_id}.txt" in the log folder.
        3. A "game_record.csv" file of all game records (if update_local is True).
        4. Updating the Google spreadsheet by appending the new game data (if update_remote is True).

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
    game_record_df = get_df_game_record(force_remote=force_remote,
                                        csv_log=csv_log,
                                        spreadsheet_id=spreadsheet_id,
                                        range_name=range_)

    # obtain current game info from the game info text file
    game_info_dict = get_game_info(game_info_file, game_record_df)

    # print out next dealer and playing information
    next_dealer_info(game_info_dict)

    if update_remote:
        # reformat dict to 2D array for writing to Google spreadsheet
        print('Updating Google spreadsheet...')
        data_in_columns = [game_info_dict[key] for key in game_info_dict.keys()]
        write_response = write_google_sheet(data_in_columns, spreadsheet_id, range_)

    if update_local:
        # reformat dict to pandas data frame
        print('Updating local game record csv...')
        game_info_df = pd.DataFrame(game_info_dict)
        new_record_df = pd.concat([game_record_df, game_info_df], axis=0)
        new_record_df.reset_index(drop=True, inplace=True)
        new_record_df.to_csv(csv_log, index=False)
        print('Local game record csv file updated.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("game_info_file", nargs='?',
                        help="optional; path to txt file of current game info.",
                        default='current_game.txt')
    parser.add_argument("-f", "--force_remote", nargs='?', type=bool,
                        help="optional; whether to force pulling data from Google spreadsheet",
                        default=False)
    args = parser.parse_args()

    if args.force_remote is None:
        force_remote = True
    else:
        force_remote = args.force_remote

    add_game_record(args.game_info_file, force_remote)
