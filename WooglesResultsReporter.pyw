import requests
import json
import csv
import PySimpleGUI as sg
import time

URL = 'https://woogles.io/twirp/tournament_service.TournamentService/GetTournamentMetadata'
URL2 = 'https://woogles.io/twirp/tournament_service.TournamentService/RecentGames'

# Define the window's contents
layout = [[sg.Radio('Tournament', 'RADIO1', default=True), sg.Radio('Club', 'RADIO1')],#[sg.Listbox(['tournament', 'club'], size=(10,2), key='-CLUB-')],
    [sg.Text('Tournament or club ID')], [sg.InputText(key='-ID-', size=(20,1))],
    [sg.Text('Number of games (1 second per 20 games)')], [sg.Slider(key='-NUMGAMES-', range=(1, 200), orientation='h', size=(34, 20), default_value=20)],
    [sg.Text('Offset (no. of games to skip from the most recent)')], [sg.Slider(key='-OFFSET-', range=(0, 500), orientation='h', size=(34, 20), default_value=0)],
    [sg.Checkbox('Append to file (overwrites if unchecked)', key='-APPEND-', default=False)], 
    [sg.Button('Get data!')]]

# Create the window
global window
window = sg.Window('Woogles Results Reporter', layout)


# Display and interact with the Window using an Event Loop
while True:
    global event, values
    
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Get data!':
        if values['-ID-'] == "":
            sg.popup('Fill in a tournament or club ID!')
            continue
        client = requests.session()
        if values[0]: t = 'tournament'
        else: t = 'club'
        headers = {
                     'slug' : '/' + t + '/' + str(values['-ID-']),
                     'encode' : 'json'
            }
        r = client.post(URL, json = headers)
        loaded = json.loads(r.content)
        numGames = int(values['-NUMGAMES-'])
        offset = int(values['-OFFSET-'])
        write_mode = 'w' if values['-APPEND-'] == False else 'a'
        try: loaded['id']
        except:
            sg.popup('Invalid tournament or club ID!')
            continue
        while numGames > 0:
            get_data = {
                     'id' : loaded['id'],
                     'numGames' : min(20, numGames), #query limited to 20
                     'offset' : offset
            }

            r = client.post(URL2, json = get_data)
            data = json.loads(r.content)
            try:
                with open('results.csv', mode=write_mode, newline = '') as outfile:
                        results_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        if write_mode == 'w':
                            results_writer.writerow(["Game ID", "Winner", "Winner's Score", "Opponent", "Opponent's Score", "End Reason"])
                        for game in data['games']:
                            if game['players'][0]['result']=='WIN':
                                winner = game['players'][0]['username']
                                winscore = game['players'][0]['score']
                                loser = game['players'][1]['username']
                                losescore = game['players'][1]['score']
                            else: #loss or tie
                                loser = game['players'][0]['username']
                                losescore = game['players'][0]['score']
                                winner = game['players'][1]['username']
                                winscore = game['players'][1]['score']

                            results_writer.writerow([game['game_id'], winner, winscore, loser, losescore, game['end_reason']])
            except:
                sg.popup('Error writing to file! Make sure that results.csv is not open.')
                break
            finally:
                numGames -= 20
                write_mode = 'a'
                offset += 20
                time.sleep(1)
        else: #executes only if numGames<=0
            sg.popup('Data extracted to results.csv!')
# Finish up by removing from the screen
window.close()
    
