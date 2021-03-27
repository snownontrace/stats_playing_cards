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
    report the next dealer information and level to play
    '''
    current_dealer_index = game_info_dict['is_dealer'].index('Yes')
    n = len(game_info_dict['is_dealer'])
    for i in range(current_dealer_index+1,
                   current_dealer_index+len(game_info_dict['is_dealer'])):
        if game_info_dict['dealer_win_lose'][0] == 'win':
            if game_info_dict['on_dealer_team'][i%n] == 'Yes':
                print('Congrats to the dealer team!')
                next_dealer = game_info_dict['player_id'][i%n]
                print('Next dealer is:', next_dealer.replace('_', ' '))
                print('We are playing:', game_info_dict['level_after'][i%n],
                      'of round', game_info_dict['level_rounds_after'][i%n])
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
    '''

    # provide default values for optional parameters
    if csv_log is None:
        csv_log = './log/game_record_test.csv'

    if spreadsheet_id is None:
        # This is the testing Google spreadsheet
        spreadsheet_id = '1GcPjxs5PaK7atFxVq4VFp94j4RlJf1z1HFlyGQmiYsw'

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
        data_in_columns = [game_info_dict[key] for key in game_info_dict.keys()]
        write_response = write_google_sheet(data_in_columns, spreadsheet_id, range_)

    if update_local:
        # reformat dict to pandas data frame
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
