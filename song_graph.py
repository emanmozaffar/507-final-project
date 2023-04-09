import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import networkx as nx
import matplotlib.pyplot as plt
import os

os.environ['SPOTIPY_CLIENT_ID'] = open("id.txt", "r").read().strip('\n')
os.environ['SPOTIPY_CLIENT_SECRET'] = open("key.txt", "r").read().strip('\n')
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:5000/callback'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope='playlist-modify-public'))
SIMILARITY_THRESHOLD = 0.7

class Song:
    def __init__(self, title, track_id, artist, genres, features):
        self.title = title
        self.track_id = track_id
        self.artist = artist
        self.genres = genres
        self.features = features

    def __str__(self):
        return f"{self.title} ({self.track_id})"

# Define the playlist IDs for each genre
playlists = [
    '37i9dQZF1DXcZDD7cfEKhW',
    '37i9dQZF1DX0XUsuxWHRQd',
    '37i9dQZF1DXcF6B6QPhFDv',
    '37i9dQZF1DX1lVhptIYRda',
    '37i9dQZF1DWZeKCadgRdKQ',
    '37i9dQZF1DWWBHeXOYZf74',
    '37i9dQZF1DX4SBhb3fqCJd',
    '37i9dQZF1DWWxrt1tiKYiX',
    '37i9dQZF1DWYBO1MoTDhZI',
    '37i9dQZF1DX1UnoGuyf388'
]

# Fetch track IDs from each playlist and add to cache

def make_cache(filename):
    track_ids = []
    song_list = []
    for playlist_id in playlists:
        playlist = sp.playlist(playlist_id)
        for track in playlist['tracks']['items']:
            track_ids.append(track['track']['id'])

    for track_id in track_ids:
        song = {}
        track = sp.track(track_id)
        artist_id = track['artists'][0]['id']

        song['title'] = track['name']
        song['track_id'] = track_id
        song['artist'] = track['artists'][0]['name']
        song['genres'] = sp.artist(artist_id)['genres']
        song['audio_features'] = sp.audio_features(track_id)[0]
        song_list.append(song)

    with open(filename, 'w+') as f:
        json.dump(song_list, f, indent=2)

# Function to load caches
def load_caches():
    """
    Loads data from caches in JSON
    format into dictionary objects.

    Returns
    -------
    tuple
        cache : dict
            A dictionary representing the cache.

    """
    f = open('tracks.json')
    cache = json.load(f)
    return cache


def song_similarity(song1, song2):
    genre_similarity = len(set(song1.genres).intersection(song2.genres)) / len(set(song1.genres).union(song2.genres))
    danceability_similarity = 1 - abs(song1.danceability - song2.danceability)
    energy_similarity = 1 - abs(song1.energy - song2.energy)

    # Calculate the average similarity score
    return (genre_similarity + danceability_similarity + energy_similarity) / 3


if __name__ == '__main__':
    # Load caches
    if os.path.isfile('tracks.json'):
        song_cache = load_caches()
    else:
        make_cache('tracks.json')
        song_cache = load_caches()

    song_list = []
    for song in song_cache:
        pass # create Song

    # Create a NetworkX graph
    G = nx.Graph()

    # Add nodes to the graph
    for song in song_list:
        G.add_node(song.title)

    # Connect nodes based on similarity score
    for song1 in song_list:
        for song2 in song_list:
            if song1 != song2:
                similarity = song_similarity(song1, song2)
                if similarity >= SIMILARITY_THRESHOLD:
                    G.add_edge(song1.title, song2.title, weight=similarity)

    # Draw the graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_color='lightblue', font_size=10)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)
    plt.show()