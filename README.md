# Spotify Playlist Maker

## Pick a vibe, any vibe, and enjoy the playlist I generate for you!

Welcome to Eman's Spotify playlist generator! The purpose of this program is pretty straightforward: Authenticate using your Spotify account, select one of five moods, and the application will automatically generate a playlist with ten tracks for you based on what you asked for. You can ask for as many playlists as you want by selecting other moods as well. Happy listening!

## Required packages

In order to run this application locally, you must have Python installed along with several of the included libraries (os, json, random, etc.) but the additional packages you'll need include NetworkX (for building graph data structures), Spotipy (for interacting with the Spotify API to pull down data and create playlists), and Flask (used to create and run the app with a user interface).

## Instructions for running code

You will need to download all files in this repository to run this program locally. Create two files in the same directory - *id.txt* and *key.txt*, and put your client secret and client ID in both of these text files. The app will automatically use these credentials to be able to access Spotify. From the terminal, navigate to the folder where the program is stored, and run these two commands in order: *export FLASK_APP=app* and *flask run* and navigate to the provided URL in your web browser. Authenticate using Spotify (this should pop up automatically) and then interact with the app to create as many playlists as you would like!

To interact with the program, you can directly do so by using your web browser, selecting your mood from the drop-down menu, and hit the button to generate the playlist. If you navigate to your Spotify account, you will see the playlist appear in your library as soon as you run the program.

## How it works

In sum, what the program does is use the Spotify API to gather track information from several popular Spotify playlists, and caches the data to access it instantaneously. Using this track information, the program constructs a graph, where the nodes are the tracks, and edges are created between tracks if they meet a defined similarity threshold. This graph is also pickled to preserve the data structure and improve efficiency.

Every Spotify track has several attributes attached to its ID: its valence (positivity), acousticness, speechiness, tempo, genre, and so on. Most of these attributes are numeric. In order to calculate track similarity, I calculate the Jaccard similarity between every value. Then, I set thresholds to define what a "happy" track is, for example, and then I filtered all of the tracks into different categories. In order to generate the playlist based on mood, I randomly select ten songs and append them to a playlist, and save it to the user's profile.

If I were to maintain this program in the long term, I would likely have it automatically 'refresh' the cache weekly, so we can update the tracks being pulled in to generate fresh playlists based on what the new releases are. I would also try to expand the number of moods to select, and see if I can make a similarity function that performs even more effectively after doing more research on how to distinguish tracks. I will likely update this repo in the future to work on these features, in addition to hosting the app itself on PythonAnywhere.
