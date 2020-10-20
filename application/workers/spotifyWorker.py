from application.workers.Spotify import SpotifyAPI
from flask import current_app, session
from dotenv import load_dotenv
from pathlib import Path
from os import getenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

if current_app:
    oauth_token = session['oauth']['access_token']
    oauth_type = session['oauth']['token_type']
else:
    oauth_token = getenv('spotify_oauth_token')
    oauth_type = getenv('spotify_oauth_type')

sp = SpotifyAPI(oauth_token, oauth_type)

def get_spotify_link(track_name):
    # sp.simple_auth()
    res = sp.find_track(track_name)
    return {'success': len(res) > 0, 'result': res.get('uri')}