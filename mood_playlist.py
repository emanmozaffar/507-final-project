import os
import json
import random
import networkx as nx
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth

# Set up Spotify API credentials
SPOTIPY_CLIENT_ID = open("id.txt", "r").read().strip('\n')
SPOTIPY_CLIENT_SECRET = open("key.txt", "r").read().strip('\n')
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

# Playlist IDs
PLAYLIST_IDS = [
    '37i9dQZF1DXcZDD7cfEKhW', '37i9dQZF1DX0XUsuxWHRQd', '37i9dQZF1DXcF6B6QPhFDv',
    '37i9dQZF1DX1lVhptIYRda', '37i9dQZF1DWZeKCadgRdKQ', '37i9dQZF1DWWBHeXOYZf74',
    '37i9dQZF1DX4SBhb3fqCJd', '37i9dQZF1DWWxrt1tiKYiX', '37i9dQZF1DWYBO1MoTDhZI',
    '37i9dQZF1DX1UnoGuyf388'
]

CACHE_FILE = 'track_cache.json'
GRAPH_FILE = 'track_graph.gpickle'

def authenticate_user():
    scope = 'playlist-modify-public'
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=scope
    )

    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        print(f'Please navigate to the following URL in your browser: {auth_url}')
        response = input('Enter the URL you were redirected to: ')
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)

    token = token_info['access_token']
    sp = spotipy.Spotify(auth=token)
    user_id = sp.current_user()['id']
    return sp, user_id

def load_or_generate_cache(sp):
    """
    Load track data from cache file or generate the cache if it doesn't exist.

    Parameters
    ----------
    sp : spotipy.Spotify
        An authenticated Spotify client object.

    Returns
    -------
    dict
        A dictionary containing track data keyed by track IDs.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            tracks = json.load(f)
    else:
        tracks = {}
        for playlist_id in PLAYLIST_IDS:
            offset = 0
            while True:
                results = sp.playlist_tracks(playlist_id, offset=offset, fields='items.track.id,items.track.name,items.track.artists,next')
                for item in results['items']:
                    track = item['track']
                    track_id = track['id']
                    track_name = track['name']
                    artist_name = track['artists'][0]['name']
                    audio_features = sp.audio_features([track_id])[0]
                    if audio_features:
                        tracks[track_id] = {
                            'name': track_name,
                            'artist': artist_name,
                            'features': audio_features
                        }
                if results['next'] is None:
                    break
                offset += len(results['items'])

        with open(CACHE_FILE, 'w') as f:
            json.dump(tracks, f)
    return tracks


def similarity(track1, track2):
    """
    Calculate the similarity between two tracks based on their audio features.

    Parameters
    ----------
    track1 : dict
        The audio features for the first track.
    track2 : dict
        The audio features for the second track.

    Returns
    -------
    float
        The similarity score between the two tracks (0 to 1).
    """
    features1 = track1['features']
    features2 = track2['features']
    energy_diff = abs(features1['energy'] - features2['energy'])
    tempo_diff = abs(features1['tempo'] - features2['tempo']) / 100
    valence_diff = abs(features1['valence'] - features2['valence'])
    loudness_diff = abs(features1['loudness'] - features2['loudness']) / 10
    return 1 - (energy_diff + tempo_diff + valence_diff + loudness_diff) / 4

def build_track_graph(tracks, similarity_threshold):
    """
    Build a NetworkX graph of tracks connected by similarity.

    Parameters
    ----------
    tracks : dict
        A dictionary containing track data keyed by track IDs.
    similarity_threshold : float
        The minimum similarity required for two tracks to be connected.

    Returns
    -------
    networkx.Graph
        A NetworkX graph with tracks as nodes and similarity as edge weights.
    """
    if os.path.exists(GRAPH_FILE):
        G = nx.read_adjlist(GRAPH_FILE, nodetype=str)
        for node, data in tracks.items():
            G.nodes[node].update(data)

        for u, v, weight in G.edges.data('weight', default=None):
            if weight is None:
                track1 = tracks[u]
                track2 = tracks[v]
                sim = similarity(track1, track2)
                G[u][v]['weight'] = sim
    else:
        G = nx.Graph()
        track_ids = list(tracks.keys())
        for track_id in track_ids:
            G.add_node(track_id, **tracks[track_id])

        for i in range(len(track_ids)):
            for j in range(i + 1, len(track_ids)):
                track1 = tracks[track_ids[i]]
                track2 = tracks[track_ids[j]]
                sim = similarity(track1, track2)
                if sim >= similarity_threshold:
                    G.add_edge(track_ids[i], track_ids[j], weight=sim)

        nx.write_adjlist(G, GRAPH_FILE)
    return G

def get_user_mood():
    """
    Get the user's mood by prompting them to choose from a list of options.

    Returns
    -------
    str
        The user's chosen mood option.
    """
    moods = ['happy', 'sad', 'chill', 'high-energy', 'surprise me']
    print('Choose a mood:')
    for i, mood in enumerate(moods):
        print(f'{i + 1}. {mood}')
    choice = int(input('Enter the number of your mood choice: '))
    return moods[choice - 1]

def filter_tracks_by_mood(tracks, mood):
    filtered_tracks = []

    for track_id, track_data in tracks.items():
        audio_features = track_data['features']

        if mood == 'happy':
            if audio_features['valence'] > 0.7:
                filtered_tracks.append(track_id)
        elif mood == 'sad':
            if audio_features['valence'] < 0.3:
                filtered_tracks.append(track_id)
        elif mood == 'chill':
            if audio_features['tempo'] < 100 and audio_features['loudness'] < -10:
                filtered_tracks.append(track_id)
        elif mood == 'high-energy':
            if audio_features['energy'] > 0.7 and audio_features['danceability'] > 0.7:
                filtered_tracks.append(track_id)
        else:  # 'surprise me'
            filtered_tracks.append(track_id)

    return filtered_tracks

def generate_playlist(tracks, mood, graph):
    """
    Generate a playlist of 10 songs based on the user's mood.

    Parameters
    ----------
    tracks : dict
        A dictionary containing track data keyed by track IDs.
    mood : str
        The user's chosen mood option.
    graph : networkx.Graph
        A NetworkX graph with tracks as nodes and similarity as edge weights.

    Returns
    -------
    list
        A list of 10 track IDs that make up the generated playlist.
    """
    filtered_tracks = filter_tracks_by_mood(tracks, mood)
    playlist = []

    if mood == 'surprise me':
        playlist = random.sample(filtered_tracks, 10)
    else:
        start_node = random.choice(filtered_tracks)
        visited = {start_node}
        playlist.append(start_node)

        for _ in range(9):
            neighbors = [neighbor for neighbor in graph.neighbors(start_node) if neighbor not in visited]
            if not neighbors:
                break
            start_node = max(neighbors, key=lambda neighbor: graph[start_node][neighbor]['weight'])
            visited.add(start_node)
            playlist.append(start_node)

        if len(playlist) < 10:
            remaining_tracks = [track for track in filtered_tracks if track not in visited]
            playlist.extend(random.sample(remaining_tracks, 10 - len(playlist)))

    return playlist

def save_playlist(sp, user_id, playlist_name, track_ids):
    """
    Save the generated playlist to the user's Spotify account.

    Parameters
    ----------
    sp : spotipy.Spotify
        An authenticated Spotify client object.
    playlist : list
        A list of 10 track IDs that make up the generated playlist.

    Returns
    -------
    None
    """
    playlist = sp.user_playlist_create(user_id, playlist_name)
    sp.user_playlist_add_tracks(user_id, playlist['id'], track_ids)
    print(f'Successfully created playlist "{playlist_name}" with {len(track_ids)} tracks.')

def main():
    """
    Executes main program.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    sp, user_id = authenticate_user()
    tracks = load_or_generate_cache(sp)
    graph = build_track_graph(tracks, similarity_threshold=0.7)
    mood = get_user_mood()
    playlist = generate_playlist(tracks, mood, graph)
    save_playlist(sp, user_id, f"{mood.capitalize()} Mood Playlist", playlist)

if __name__ == "__main__":
    main()
