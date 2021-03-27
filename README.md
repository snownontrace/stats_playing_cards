## Instructions to add new game records

1. Install Python and at least the numpy and pandas libraries.

    - If you are new to Python, the easiest is probably to [install Anaconda](https://www.anaconda.com/products/individual), which comes with a large number of commonly used libraries.

1. Clone [this repository](https://github.com/snownontrace/stats_playing_cards).

    - If you are familiar with Git, `cd` to a folder where you want to store scripts, and run the following command in a shell. This will create a folder called "stats_playing_cards" that contains all scripts and supporting files.

      ```bash
      git clone https://github.com/snownontrace/stats_playing_cards
      ```

    - If you don't know what Git is, visit [this webpage](https://github.com/snownontrace/stats_playing_cards), click the green button "Code" to expand the dropdown menu and then click "Download ZIP" to download the repository as a compressed bundle. Unzip it somewhere and you will have a "stats_playing_cards-main" folder that contains all scripts and supporting files.

1. Follow instructions [here](https://developers.google.com/sheets/api/quickstart/python) to enable Google Sheets API and install the Google Client Library.

    - Put the credentials.json file in the repository folder ("stats_playing_cards" or "stats_playing_cards-main") you made in the last step.

1. Run `python add_game_record_test.py` in a shell to see if you have successfully added new game information as specified in the text file "current_game.txt" to the [testing Google spreadsheet](https://docs.google.com/spreadsheets/d/1GcPjxs5PaK7atFxVq4VFp94j4RlJf1z1HFlyGQmiYsw/edit?usp=sharing).

    - The first time you run this script, it will open a webpage asking you to authorize the access to your Google sheets. Once you give permission, it will create a "token.pickle" file in the folder. As long as the pickle file is there, you don't need to re-do the authorization.

1. If the testing run is successful, you should see new lines of data added to the [testing Google spreadsheet](https://docs.google.com/spreadsheets/d/1GcPjxs5PaK7atFxVq4VFp94j4RlJf1z1HFlyGQmiYsw/edit?usp=sharing).

1. Now you are all set to go! In future games, all you need to do is to edit "current_game.txt" and run `python add_game_record.py` to add new game record.

    - By default, add_game_record.py will first try to use the local game_record.csv in the log folder. If it is not there, it will pull data from the Google spreadsheet.
    - You can also force the script to use data from the remote source (i.e.Google spreadsheet) by adding a '-f' flag (`python add_game_record.py -f`). This is useful when you have taken over the recording responsibility from another player and your local record is clearly not up to date.
