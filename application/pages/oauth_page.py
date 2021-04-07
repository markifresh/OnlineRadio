from flask import redirect, url_for, Blueprint, request, current_app, session
from config import SpotifyConfig, DeezerConfig
from json import loads as json_loads
from requests import post as req_post
from urllib.parse import urlencode
from datetime import datetime, timedelta

from application.music_services.Spotify import Spotify
from application.music_services.Deezer import Deezer
from application.db_models.user import User

oauth = Blueprint('oauth', __name__, template_folder='templates')


def redirect_to_previous_page():
    return request.referrer if request.referrer else url_for('oauth.auth')

@oauth.route('/auth')
def auth():
    last_login = datetime.now()
    account_uri = session['ms_user']['uri']
    user = User.query(User).filter(User.account_uri == account_uri)

    user_dict = {
        'last_login': last_login,
        'account_uri': account_uri
    }
    if user.count() == 0:
        user_dict['service_name'] = session['ms_service']
        user_dict['display_name'] = session['ms_user']['display_name']
        user_dict['account_id'] = session['ms_user']['id']
        res = User.commit_data(user_dict)
        if not res['success']:
            return res
        user = User.query(User).filter(User.account_uri == account_uri)

    user = user.first()
    user.session.close()

    if not user.radios:
        session['configured'] = False
        return redirect(url_for('user_settings.show_settings'))

    session['configured'] = True
    User.update_row(user_dict)
    return redirect(url_for('radios.radios_list'))




@oauth.route('/spotify')
def spotify_redirect():
    session.permanent = True
    params = urlencode({
        'client_id': SpotifyConfig.CLIENT_ID,
        'scope': SpotifyConfig.SCOPE,
        'redirect_uri': url_for('oauth.spotify_callback', _external=True).replace('localhost', '127.0.0.1'),
        'response_type': 'code'
    })

    auth_url = f'{SpotifyConfig.SPOTIFY_AUTH_URL}/?{params}'
    return redirect(auth_url)


@oauth.route('/spotify/callback')
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
        return {'success': False, 'result': post_request.text}

    response_data = json_loads(post_request.text)
    sp = Spotify(token=response_data['access_token'], expires_in_sec=response_data['expires_in'])
    user_data = sp.get_user_info()
    if not user_data['success']:
        return {'success': False, 'result': 'Failed to get user data'}

    session['logged_in'] = True
    session['ms_user'] = user_data['result']
    session['ms_service'] = 'spotify'
    session['oauth'] = response_data
    session['oauth']['expiration_time'] = datetime.now() + timedelta(seconds=response_data['expires_in'])

    return redirect(url_for('oauth.auth'))



@oauth.route('/deezer')
def deezer_redirect():
    session.permanent = True
    params = urlencode({
        'app_id': DeezerConfig.CLIENT_ID,
        'perms': DeezerConfig.SCOPE,
        'redirect_uri': url_for('oauth.deezer_callback', _external=True).replace('127.0.0.1', 'localhost')
    })

    auth_url = f'{DeezerConfig.DEEZER_AUTH_URL}/?{params}'
    return redirect(auth_url)


@oauth.route('/deezer/callback')
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


    dz = Deezer(token, expires_in)
    user_data = dz.get_user_info()
    if not user_data['success']:
        return {'success': False, 'result': 'Failed to get user data'}

    session['logged_in'] = True
    session['ms_user'] = user_data['result']
    session['ms_service'] = 'deezer'
    session['oauth'] = {'token': token,
                        'expiration_time': datetime.now() + timedelta(seconds=expires_in)}

    return redirect(url_for('oauth.auth'))