import os
import pandas as pd
import numpy as np
from read_google_sheet import read_google_sheet
from datetime import date

def parse_game_info(game_info_file):
    '''
    Read in lines of current game info, parse lines of text to a dictionary

    Input
    -----
    game_info_file: a text file storing current game info

    Returns
    -------
    A dictionary storing current game information

    '''

    with open(game_info_file, 'r') as f:
        lines = f.readlines()

    game_info = {}
    for line in lines:
        # skip comment lines, empty lines and lines without ':'
        if line.startswith('#') or line.strip(' \t\n')=='' or not (':' in line):
#             print('skipped')
            continue
        else:
            game_info_key = line.split(':')[0].strip()
            game_info_list = line.split(':')[1].strip(' \t\n').split(',')
            game_info_list_cleaned = [i.strip().replace(' ', '_') for i in game_info_list]
            if game_info_key in ['n_decks', 'score_goal', 'score']:
                game_info[game_info_key] = [int(game_info_list_cleaned[0])]
            else:
                game_info[game_info_key] = game_info_list_cleaned

    return game_info


def get_lifetime_level_before(player, df_game_record):
    '''
    Get the previous cumulative level (lifetime_level_before) for player

    Input
    -----
    player: the palyer to query
    df_game_record: a pandas data frame storing the game history,
                    must have 'player_id' and 'lifetime_level_after'

    Returns
    -------
    lifetime_level_before:
        if new player, return 0
        if old player, return the last item of the column
            "lifetime_level_after" in the record of this player

    '''
    assert 'player_id' in df_game_record.columns
    assert 'lifetime_level_after' in df_game_record.columns

    df_player = df_game_record[df_game_record.player_id==player]

    if len(df_player) == 0:
        # new player, initialize with 0
        lifetime_level_before = 0
    else:
        lifetime_level_before = df_player.lifetime_level_after.tolist()[-1]

    return lifetime_level_before


def next_game_id(df_game_record):
    '''
    Returns the next game_id by incrementing the last game_id in game_record
    '''
    assert 'game_id' in df_game_record.columns

    return df_game_record.game_id.tolist()[-1] + 1


def get_level_up(game_info):
    '''
    Input
    -----
    game_info: dictionary storing game information; requires 'score' and 'score_goal'

    Returns
    -------
    level_up: integer of levels to go up for the winning team
    '''
    assert 'score' in game_info.keys()
    assert 'score_goal' in game_info.keys()

    # level_up
    if game_info['score'][0] < game_info['score_goal'][0]:
        # when dealer team wins
        score_diff = game_info['score_goal'][0] - game_info['score'][0] - 1
        level_up = (score_diff - score_diff%20) / 20 + 1
    else:
        # when dealer team loses
        score_diff = game_info['score'][0] - game_info['score_goal'][0]
        level_up = (score_diff - score_diff%20) / 20

    return int(level_up)


def get_level_current_round(life_time_level, n_steps=14):
    '''
    Calculate equivalent level at current round from life_time_level and steps per round

    Default n_steps is 14, including a "wuzhu" level. Use 13 to skip "wuzhu"

    '''
    level = str(life_time_level%n_steps + 2)
    if level == '11':
        level = 'J'
    if level == '12':
        level = 'Q'
    if level == '13':
        level = 'K'
    if level == '14':
        level = 'A'
    if level == '15':
        level = 'wuzhu'

    return level


def get_level_rounds(life_time_level, n_steps=14):
    '''
    Calculate level rounds given life_time_level and steps per round

    Default n_steps is 14, including a "wuzhu" level. Use 13 to skip "wuzhu"

    '''
    level_rounds = (life_time_level - life_time_level%n_steps)/n_steps + 1

    return int(level_rounds)


def get_df_game_record(force_remote=False, csv_log=None, spreadsheet_id=None, range_name=None):
    '''

    Parameters
    ----------

    csv_log:
        A local spreadsheet of past game record.
        Default: './log/game_record.csv'

    spreadsheet_id:
        The identifier of a spreadsheet, which is embedded in the Google Spreadsheet URL.
        For example:
            https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid={sheet_id}
        Defalt: '1So3PBr9gV3I0LzApZOgJlQew2QjM1wAiWhR50rAnHRg' (game record spreadsheet)

    range_name:
        Specify the range of data. For example: 'Sheet1!A1:E5'
        Defalt: 'Sheet1'


    Returns
    -------

    df:
        A pandas data frame storing past game record.


    Other Outputs
    -------------

    If a local game record is not already there, write a spreadsheet to the path of csv_log.


    '''

    # provide default values for optional parameters
    if csv_log is None:
        csv_log = './log/game_record.csv'

    if spreadsheet_id is None:
        # This is the Google spreadsheet hosting the game record
        spreadsheet_id = '1So3PBr9gV3I0LzApZOgJlQew2QjM1wAiWhR50rAnHRg'

    if range_name is None:
        # This is the sheet name of the Google spreadsheet file
        range_name = 'Sheet1'

    if (not force_remote) and os.path.isfile(csv_log):
        df = pd.read_csv(csv_log)
    else:
        print('Local game record not found or force_remote enabled. Pulling from Google spreadsheet...')
        data = read_google_sheet(spreadsheet_id, range_name)

        # Reformat the data into a pandas dataframe
        df_raw = pd.DataFrame(data[1:], columns=data[0])

        # change the data types of certain columns to integers for calculation
        df = df_raw.astype({'game_id': 'int64',
                            'level_rounds_before': 'int64',
                            'level_rounds_after': 'int64',
                            'score_goal': 'int64',
                            'n_players': 'int64',
                            'n_decks': 'int64',
                            'score': 'int64',
                            'level_up': 'int64',
                            'lifetime_level_before': 'int64',
                            'lifetime_level_after': 'int64',
                            'year': 'int64',
                            'month': 'int64',
                            'day': 'int64'})

        # make sure the parental folder exists, when the file is not yet there
        if not os.path.isdir( os.path.dirname(csv_log) ):
            os.mkdir( os.path.dirname(csv_log) )

        # write to the csv log file
        df.to_csv(csv_log, index=False)

    return df


def get_game_info(game_info_file, game_record_df=None, keep_game_info_log=None):
    '''
    Parameters
    ----------

    game_info_file:
        Path to a text file storing current game information.
        Each line has the format:
            [descriptor]: [content separated by commas]
        Lines beginning with '#' and empty lines will be ignored.

    game_record_df:
        A pandas data frame storing past game record.
        Default: obtained from get_df_game_record()


    Returns
    -------

    game_info_dict:
        A dictionary of new game info from the game_info_file.
            - The keys are exactly the column names in the pandas data frame game_record_df.
            - The value of the key is a list of same length as the number of players.
            - If info is not available, the value is filled with 'NA's.

    '''

    if game_record_df is None:
        game_record_df = get_df_game_record()

    if keep_game_info_log is None:
        keep_game_info_log = True

    # read in game_info from text file
    game_info = parse_game_info(game_info_file)

    # game_id
    game_id = next_game_id(game_record_df)
    game_info['game_id'] = [game_id]

    if keep_game_info_log:
        log_folder = os.path.join(os.path.dirname(game_info_file), 'log')
        if not os.path.isdir(log_folder):
            os.mkdir(log_folder)
        log_file = os.path.join(log_folder, 'game_log_' + str(game_id) + '.txt')
        with open(game_info_file, 'r') as f:
            lines = f.readlines()
        with open(log_file, 'w') as f:
            for line in lines:
                f.write(line)

    # player_id
    game_info['player_id'] = game_info['players']

    # is_dealer status
    game_info['is_dealer'] = ['Yes' if i in game_info['dealer'] else 'No'
                              for i in game_info['players']]

    # on_dealer_team status
    dealer_team_list = game_info['dealer'] + game_info['dealer_team']
    game_info['on_dealer_team'] = ['Yes' if i in dealer_team_list else 'No'
                                   for i in game_info['players']]

    # dealer_win_lose status
    game_info['dealer_win_lose'] = ['win' if game_info['score'][0]<game_info['score_goal'][0]
                                    else 'lose']

    # non_dealer_win_lose status
    game_info['non_dealer_win_lose'] = ['lose' if game_info['score'][0]<game_info['score_goal'][0]
                                        else 'win']

    # player_win_lose status
    if game_info['score'][0] < game_info['score_goal'][0]:
        game_info['player_win_lose'] = ['win' if x=='Yes' else 'lose'
                                        for x in game_info['on_dealer_team']]
    else:
        game_info['player_win_lose'] = ['lose' if x=='Yes' else 'win'
                                        for x in game_info['on_dealer_team']]

    # is_MVP status
    game_info['is_MVP'] = ['Yes' if i in game_info['MVP'] else 'No'
                           for i in game_info['players']]

    # n_players
    game_info['n_players'] = [len(game_info['players'])]

    # level_up
    level_up = get_level_up(game_info)
    game_info['level_up'] = [level_up]

    # lifetime_level_before
    game_info['lifetime_level_before'] = [get_lifetime_level_before(x, game_record_df)
                                          for x in game_info['players']]

    # lifetime_level_after
    player_level_up = [int(level_up) if x=='win' else 0 for x in game_info['player_win_lose']]
    game_info['lifetime_level_after'] = [game_info['lifetime_level_before'][i] + player_level_up[i]
                                         for i in range(len(player_level_up))]

    # level_before, level_rounds_before, level_after, level_rounds_after
    game_info['level_before'] = [get_level_current_round(x)
                                 for x in game_info['lifetime_level_before']]

    game_info['level_rounds_before'] = [get_level_rounds(x)
                                        for x in game_info['lifetime_level_before']]

    game_info['level_after'] = [get_level_current_round(x)
                                 for x in game_info['lifetime_level_after']]

    game_info['level_rounds_after'] = [get_level_rounds(x)
                                       for x in game_info['lifetime_level_after']]

    # year, month, day
    game_info['year'] = [date.today().year]
    game_info['month'] = [date.today().month]
    game_info['day'] = [date.today().day]

    # Expand list of single-item entry
    for key in game_info.keys():
        if len(game_info[key])==1:
            game_info[key] = game_info[key]*len(game_info['players'])

    game_info_dict = {}
    for col in game_record_df.columns:
        if col not in game_info.keys():
            game_info_dict[col] = ['NA']*len(game_info['players'])
        else:
            game_info_dict[col] = game_info[col]

    return game_info_dict
