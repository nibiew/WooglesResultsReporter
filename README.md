# Woogles Results Reporter
A basic tool to grab Woogles tournament/club results into a .csv format ("results.csv" in the same folder), to facilitate tournament organisers. You can run the .exe file from the .zip or run the code directly if you have Python installed.

## Instructions

	1. Select "Tournament" to extract results from a tournament lobby, or "Club" to extract results from a club lobby.
	
	2. Fill in the tournament or club id - so "coco-blitz" if you're extracting data from the BlitzChamps tournament pool play matches.
	
	3. Select a number of games to extract, up to 500. The bot takes 1 second to extract 20 games, so as not to overload Woogles with API requests.
	
	4. (Optional) Specify an offset - this is the number of recent games the tool will skip, so if your offset is 100 and number of games to extract is 50, it will extract the 101-150 most recent games in the tournament lobby.
	
	5. (Optional) Select "Append to file" if you wish to append to an existing file. Otherwise, the tool will overwrite the existing "results.csv" file in the same folder.