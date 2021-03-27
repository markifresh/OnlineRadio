from flask import redirect, url_for, Blueprint, request, current_app, session
from config import SpotifyConfig as auth_config
from config import DeezerConfig
from json import loads as json_loads
from requests import post as req_post
from urllib.parse import urlencode
from datetime import datetime, timedelta
from application.apis.spotify_api import get_user_data
oauth_page = Blueprint('oauth', __name__, template_folder='templates')


@oauth_page.route('/spotify')
def spotify_redirect():
    session['pre_auth_page'] = request.referrer
    params = urlencode({
        'client_id': auth_config.CLIENT_ID,
        'scope': auth_config.SCOPE,
        'redirect_uri': url_for('oauth.spotify_callback', _external=True),
        'response_type': 'code'
    })

    auth_url = f'{auth_config.SPOTIFY_AUTH_URL}/?{params}'
    return redirect(auth_url)


@oauth_page.route('/spotify/callback')
def spotify_callback():
    auth_token = request.args['code']
    code_payload = {
        'grant_type': 'authorization_code',
        'code': str(auth_token),
        'redirect_uri': url_for('oauth.spotify_callback', _external=True),
        'client_id': auth_config.CLIENT_ID,
        'client_secret': auth_config.CLIENT_KEY,
    }
    post_request = req_post(auth_config.SPOTIFY_TOKEN_URL, data=code_payload)
    if post_request.status_code != 200 or 'token' not in post_request.text:
        return post_request.text

    response_data = json_loads(post_request.text)
    session['oauth'] = response_data
    session_limit = getattr(session['oauth'], 'expires_in', 3600)
    session['oauth']['expiration_time'] = datetime.now() + timedelta(seconds=session_limit)

    session['spotify_user'] = get_user_data()['result']
    print(session['oauth'])
    print(session['spotify_user'])
    return redirect(session['pre_auth_page'] )





@oauth_page.route('/deezer')
def deezer_redirect():
    session['pre_auth_page'] = request.referrer
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
    print(code_payload)

    post_request = req_post(DeezerConfig.DEEZER_TOKEN_URL, data=code_payload)
    if post_request.status_code != 200 or 'token' not in post_request.text:
        return post_request.text

    token, expires_in = post_request.text.split('&')
    token = token.split('token=')[-1]
    expires_in = int(expires_in.split('expires=')[-1])

    session['oauth'] = {'token': token,
                        'expiration_time': datetime.now() + timedelta(seconds=expires_in)}
    # session_limit = getattr(session['oauth'], 'expires_in', 3600)
    # session['oauth']['expiration_time'] = datetime.now() + timedelta(seconds=session_limit)
    #
    # session['spotify_user'] = get_user_data()['result']
    print(session['oauth'])
    # print(session['spotify_user'])
    return redirect(session['pre_auth_page'])