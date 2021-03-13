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
    [sg.Text('Number of games (1 second per 20 games)')], [sg.Slider(key='-NUMGAMES-', range=(1, 500), orientation='h', size=(34, 20), default_value=20, resolution=20)],
    [sg.Text('Offset (no. of games to skip from the most recent)')], [sg.InputText(key='-OFFSET-', size=(5,1), enable_events=True, default_text='0')],
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
    elif event == '-OFFSET-' and values['-OFFSET-'] and values['-OFFSET-'][-1] not in ('0123456789.'):
        window['-OFFSET-'].update(values['-OFFSET-'][:-1])
    elif event == 'Get data!':
        try:
            int(values['-OFFSET-'])
        except ValueError:
            sg.popup('Key in a valid number of offset!')
            continue
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
        num_games = int(values['-NUMGAMES-'])
        offset = int(values['-OFFSET-'])
        write_mode = 'w' if values['-APPEND-'] == False else 'a'
        total_games = 0
        try: loaded['id']
        except:
            sg.popup('Invalid tournament or club ID!')
            continue
        while num_games > 0:
            get_data = {
                     'id' : loaded['id'],
                     'numGames' : min(20, num_games), #query limited to 20
                     'offset' : offset
            }

            r = client.post(URL2, json = get_data)
            data = json.loads(r.content)
            if len(data['games']) < 20:
                num_games = -1 #end if no more games
            total_games += len(data['games'])
            try:
                with open('results.csv', mode=write_mode, newline = '') as outfile:
                        results_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        record = ['WIN', 'DRAW']
                        if write_mode == 'w':
                            results_writer.writerow(["Game ID", "Winner", "Winner's Score", "Opponent", "Opponent's Score", "Winner Started?", "End Reason"])
                        for game in data['games']:
                            if game['players'][0]['result'] in record: #win or tie
                                winner = game['players'][0]['username']
                                winscore = game['players'][0]['score']
                                loser = game['players'][1]['username']
                                losescore = game['players'][1]['score']
                                winner_start=True
                            else: #loss
                                loser = game['players'][0]['username']
                                losescore = game['players'][0]['score']
                                winner = game['players'][1]['username']
                                winscore = game['players'][1]['score']
                                winner_start=False
                            results_writer.writerow([game['game_id'], winner, winscore, loser, losescore, winner_start, game['end_reason']])
            except:
                sg.popup('Error writing to file! Make sure that results.csv is not open.')
                break
            finally:
                num_games -= 20
                write_mode = 'a'
                offset += 20
                time.sleep(1)
        else: #executes only if num_games<=0
            sg.popup(str(total_games) + ' games extracted to results.csv!')
# Finish up by removing from the screen
window.close()
    
