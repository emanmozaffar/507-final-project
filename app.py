import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from mood_playlist import *

app = Flask(__name__)
app.secret_key = 'your_flask_secret_key'
app.config['SESSION_COOKIE_SECURE'] = True

# Replace these with your own credentials
os.environ['SPOTIPY_CLIENT_ID'] = open("id.txt", "r").read().strip('\n')
os.environ['SPOTIPY_CLIENT_SECRET'] = open("key.txt", "r").read().strip('\n')
os.environ['SPOTIPY_REDIRECT_URI'] = 'http://127.0.0.1:5000/callback'

sp_oauth = SpotifyOAuth(scope='playlist-modify-public user-library-read')

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get("access_token"):
        return redirect(url_for("login"))

    sp = spotipy.Spotify(auth=session["access_token"])
    token_info = sp_oauth.get_access_token(as_dict=True)  # Refresh the access token if needed

    if token_info["access_token"] != session["access_token"]:
        session["access_token"] = token_info["access_token"]

    sp = spotipy.Spotify(auth=session["access_token"])

    user_id = sp.current_user()["id"]

    if request.method == "POST":
        mood = request.form["mood"]
        tracks = load_or_generate_cache(sp)
        graph = build_track_graph(tracks, similarity_threshold=0.7)
        playlist = generate_playlist(tracks, mood, graph)
        save_playlist(sp, user_id, f"{mood} vibes", playlist)
        flash("check your spotify account for a new playlist!", "success")
        return redirect(url_for("index"))

    return render_template('index.html')

@app.route('/callback')
def callback():
    code = sp_oauth.parse_response_code(request.url)
    token_info = sp_oauth.get_access_token(code)
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
