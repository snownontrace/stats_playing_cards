from get_sheet_data import get_sheet_data
import pandas as pd
from datetime import date

# Utility functions
def get_player_stats(df, player, shortstaffed_games_list):
    '''Calculate playing statistics of the specified player
    '''
    assert 'player_id' in df.columns
    assert 'player_win_lose' in df.columns
    assert 'level_up' in df.columns
    assert 'is_dealer' in df.columns
    assert player in df.player_id.to_list()

    # subset rows of the specified player
    df_player = df[df.player_id == player]

    # subset rows that this player wins
    df_player_winning = df_player[df_player.player_win_lose == 'win']

    # calculate the winning rate
    winning_rate = len(df_player_winning) / len(df_player)

    # calculate the average levels up per winning game
    if len(df_player_winning) > 0:
        average_level_up = df_player_winning.level_up.mean()
    else:
        average_level_up = 0

    # subset rows that this player is dealer
    df_player_dealing = df_player[df_player.is_dealer == 'Yes']

    # subset rows that this player is dealer and wins
    df_player_dealing_winning = df_player[(df_player.is_dealer == 'Yes') &
                                          (df_player.player_win_lose == 'win')]

    # calculate the winning rate as dealer
    if len(df_player_dealing) > 0:
        winning_rate_as_dealer = len(df_player_dealing_winning) / len(df_player_dealing)
    else:
        winning_rate_as_dealer = 0

    # calculate the number of occurrences of shortstaffed dealer team as dealer
    dealing_games_list = df_player_dealing.game_id.tolist()
    n_shortstaffed_games = len( list(set(shortstaffed_games_list) & set(dealing_games_list)) )

#     player_stats = [player,
#                     winning_rate,
#                     average_level_up,
#                     len(df_player),
#                     len(df_player_dealing),
#                     n_shortstaffed_games,
#                     winning_rate_as_dealer]

    # formatted version
    player_stats = [player.replace('_', ' '),
                    "{:.1%}".format(winning_rate),
                    "{:.2f}".format(average_level_up),
                    len(df_player),
                    len(df_player_dealing),
                    n_shortstaffed_games,
                    "{:.1%}".format(winning_rate_as_dealer)]

    return player_stats

def get_dealer_winning_rate_at_n_decks(df, n_decks):
    '''calculate the dealer's winning rate of the specified n_decks
    '''
    assert 'n_decks' in df.columns
    assert 'dealer_win_lose' in df.columns
    assert 'game_id' in df.columns

    df_n_decks = df[df.n_decks == n_decks]
    if len(df_n_decks) > 0:
        df_selected = df[(df.n_decks == n_decks) & (df.dealer_win_lose == 'win')]
        winning_rate = df_selected.game_id.nunique() / df_n_decks.game_id.nunique()
        return winning_rate
    else:
        return 'na'

def get_dealer_winning_rate_at_n_players(df, n_players):
    '''calculate the dealer's winning rate of the specified n_players
    '''
    assert 'n_players' in df.columns
    assert 'dealer_win_lose' in df.columns
    assert 'game_id' in df.columns

    df_n_decks = df[df.n_players == n_players]
    if len(df_n_decks) > 0:
        df_selected = df[(df.n_decks == n_decks) & (df.dealer_win_lose == 'win')]
        winning_rate = df_selected.game_id.nunique() / df_n_decks.game_id.nunique()
        return winning_rate
    else:
        return 'na'

def dealer_team_shortstaffed(df, game_id):
    '''determine whether the dealer team has fewer members than expected
    '''
    assert 'game_id' in df.columns
    assert 'n_players' in df.columns
    assert 'on_dealer_team' in df.columns

    df_current_game = df[df.game_id == game_id]
    df_current_game.reset_index(inplace=True)
    n_players = df_current_game.n_players[0]
    expected_dealer_team_n = (n_players-n_players%2)/2
    actual_dealer_team_n = df_current_game.groupby('on_dealer_team').describe().loc['Yes','game_id']['count']

    return actual_dealer_team_n < expected_dealer_team_n

def get_games_dealer_team_shortstaffed(df):
    '''get a list of game_id when the dealer team is shortstaffed
    '''
    assert 'game_id' in df.columns
    assert 'n_players' in df.columns
    assert 'on_dealer_team' in df.columns

    games_dealer_team_shortstaffed = []
    for game_id in df.game_id.unique():
        if dealer_team_shortstaffed(df, game_id):
            games_dealer_team_shortstaffed.append(game_id)

    return games_dealer_team_shortstaffed

# pull data from the Google spreadsheet
SHEET_URL = 'https://docs.google.com/spreadsheets/d/1So3PBr9gV3I0LzApZOgJlQew2QjM1wAiWhR50rAnHRg/edit#gid=2137801449'
spreadsheet_id = SHEET_URL.split('/')[5]
data = get_sheet_data(spreadsheet_id, 'cleaned')

# Reformat the data into a pandas dataframe
df_raw = pd.DataFrame(data[1:], columns=data[0])

# Add a column of date
df_raw['date'] = df_raw.year + '-' + df_raw.month + '-' + df_raw.day
df_raw.head()

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

# get a list of game_id when the dealer team is shortstaffed
shortstaffed_games_list = get_games_dealer_team_shortstaffed(df)

player_stats_data = []
for player in df.player_id.unique():
    player_stats_data.append(get_player_stats(df, player, shortstaffed_games_list))
player_stats_df = pd.DataFrame(player_stats_data,
                               columns=['Player',
                                        'Winning rate',
                                        'Average levels up',
                                        'N_games played',
                                        'N_games as dealer',
                                        'N_games short-staffed as dealer',
                                        'Winning rate as dealer'])

player_stats_df.sort_values(by=['Winning rate', 'Average levels up'],
                            ascending=False, inplace=True)
player_stats_df.reset_index(inplace=True, drop=True)
player_stats_df['Rank'] = list(range(1, len(player_stats_df)+1))
player_stats_df = player_stats_df[['Rank'] + player_stats_df.columns[:-1].tolist()]
# player_stats_df

# update the markdown file in the gibhub pages folder
header_file = open('../snownontrace.github.io/player_stats_header.md', 'r')
lines = header_file.readlines()

# get today's date
today = date.today()
date_today = today.strftime("%Y-%m-%d")

with open('../snownontrace.github.io/player_stats.md', 'w') as the_file:
    for line in lines[:5]:
        the_file.write(line)
    # update the date with the current date
    the_file.write('date: ' + date_today + '\n')
    for line in lines[6:-3]:
        the_file.write(line)
    for i in range(len(player_stats_df)):
        player_stats = [str(iii) for iii in player_stats_df.iloc[i,:].tolist()]
        player_stats_line = '| ' + ' | '.join(player_stats) + ' |' + '\n'
        the_file.write(player_stats_line)
    for line in lines[-2:]:
        the_file.write(line)
