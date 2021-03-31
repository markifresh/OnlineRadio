from flask import redirect, url_for, Blueprint, request, current_app, session
from config import SpotifyConfig, DeezerConfig
from application.music_services.Spotify import Spotify
from application.music_services.Deezer import Deezer
from json import loads as json_loads
from requests import post as req_post
from urllib.parse import urlencode
from datetime import datetime, timedelta

oauth_page = Blueprint('oauth', __name__, template_folder='templates')


def redirect_to_previous_page():
    return request.referrer if request.referrer else url_for('radios.radios_list')


@oauth_page.route('/spotify')
def spotify_redirect():
    params = urlencode({
        'client_id': SpotifyConfig.CLIENT_ID,
        'scope': SpotifyConfig.SCOPE,
        'redirect_uri': url_for('oauth.spotify_callback', _external=True),
        'response_type': 'code'
    })

    auth_url = f'{SpotifyConfig.SPOTIFY_AUTH_URL}/?{params}'
    return redirect(auth_url)


@oauth_page.route('/spotify/callback')
def spotify_callback():
    auth_token = request.args['code']
    code_payload = {
        'grant_type': 'authorization_code',
        'code': str(auth_token),
        'redirect_uri': url_for('oauth.spotify_callback', _external=True),
        'client_id': SpotifyConfig.CLIENT_ID,
        'client_secret': SpotifyConfig.CLIENT_KEY,
    }
    post_request = req_post(SpotifyConfig.SPOTIFY_TOKEN_URL, data=code_payload)
    if post_request.status_code != 200 or 'token' not in post_request.text:
        return post_request.text

    response_data = json_loads(post_request.text)
    sp = Spotify(token=response_data['access_token'], expires_in_sec=response_data['expires_in'])
    user_data = sp.get_user_info()
    if not user_data['success']:
        return {'success': False, 'result': 'Failed to get user data'}

    session['ms_user'] = user_data['result']
    session['ms_service'] = 'spotify'
    session['oauth'] = response_data
    session['oauth']['expiration_time'] = datetime.now() + timedelta(seconds=response_data['expires_in'])

    return redirect(redirect_to_previous_page())





@oauth_page.route('/deezer')
def deezer_redirect():
    params = urlencode({
        'app_id': DeezerConfig.CLIENT_ID,
        'perms': DeezerConfig.SCOPE,
        'redirect_uri': url_for('oauth.deezer_callback', _external=True).replace('127.0.0.1', 'localhost')
    })

    auth_url = f'{DeezerConfig.DEEZER_AUTH_URL}/?{params}'
    return redirect(auth_url)


@oauth_page.route('/deezer/callback')
def deezer_callback():
    auth_token = request.args['code']
    code_payload = {
        'code': str(auth_token),
        'app_id': DeezerConfig.CLIENT_ID,
        'secret': DeezerConfig.CLIENT_SECRET,
    }

    post_request = req_post(DeezerConfig.DEEZER_TOKEN_URL, data=code_payload)
    if post_request.status_code != 200 or 'token' not in post_request.text:
        return {'success': False, 'result': post_request.text}

    token, expires_in = post_request.text.split('&')
    token = token.split('token=')[-1]
    expires_in = int(expires_in.split('expires=')[-1])

    session['oauth'] = {'token': token,
                        'expiration_time': datetime.now() + timedelta(seconds=expires_in)}

    dz = Deezer(token, expires_in)
    user_data = dz.get_user_info()
    if not user_data['success']:
        return {'success': False, 'result': 'Failed to get user data'}

    session['ms_user'] = user_data['result']
    session['ms_service'] = 'deezer'

    return redirect(redirect_to_previous_page())