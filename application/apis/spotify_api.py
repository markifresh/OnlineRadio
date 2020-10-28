from application.workers.Spotify import SpotifyAPI
from flask import session, redirect, url_for, current_app
from dotenv import load_dotenv
from pathlib import Path
from os import getenv


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def create_obj():
    if current_app:
        oauth_token = session['oauth']['access_token']
        oauth_type = session['oauth']['token_type']
        # user_id = session['spotify_user']['id']
    else:
        oauth_token = getenv('spotify_oauth_token')
        oauth_type = getenv('spotify_oauth_type')
        # user_id = getenv('spotify_user_id')

    return SpotifyAPI(oauth_token, oauth_type)


def get_spotify_link(track_name):
    return create_obj().find_track(track_name)


def get_user_data():
    return create_obj().get_user_data()


def get_radios_playlists():
    return create_obj().get_radios_playlists()


def get_radio_playlist(playlist_id):
    return create_obj().get_user_playlist_by_id(playlist_id)


def create_playlist(name):
    return create_obj().create_user_playlist(name)


def modify_playlist(playlist_id, name='', description='', public=''):
    return create_obj().change_user_playlist(playlist_id, name, description, public)


def get_playlist_tracks(playlist_id):
    return create_obj().get_playlist_tracks(playlist_id)


def add_tracks_to_playlist(playlist_name, tracks):
    return create_obj().add_tracks_to_playlist(playlist_name, tracks)

def mark_tracks_reviewed():
    # 1) check all tracks in DB with spotify URI and not reviewed
    # 2) get all tracks in playlists --> get list of URIs
    # 3) for track in DB tracks: if track not in playlists_tracks --> mark as reviewed
    pass

def get_token():
    return redirect(url_for('oauth_page.spotify_redirect'))


def refresh_token(refresh_token):
    return create_obj().refresh_token(refresh_token)

