from application.music_services.MSAbstract import MSAbstract
from application.pages.oauth_page import spotify_redirect
from urllib.parse import quote, urlencode
from config import SpotifyConfig
from requests import get, post, put
from json import loads as json_loads
from base64 import b64encode
from datetime import datetime, timedelta


class Spotify(MSAbstract):
    api_url = SpotifyConfig.SPOTIFY_API_URL
    tracks_search_limit = SpotifyConfig.TRACKS_SEARCH_LIMIT
    oath_headers = {}
    server_usage = True

    def __init__(self, token='', expires_in_sec=0):
        if not token:
            self.set_service_token()
        else:
            self.server_usage = False
            self.oath_headers = {'Authorization': f'Bearer {token}'}
            self.token_expiration_time = datetime.now() + timedelta(seconds=int(expires_in_sec))

    def create_service_token(self):
        message = SpotifyConfig.CLIENT_ID + ':' + SpotifyConfig.CLIENT_KEY
        message_bytes = message.encode('ascii')
        base64_bytes = b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        url = SpotifyConfig.SPOTIFY_TOKEN_URL
        data = {'grant_type': 'client_credentials'}
        headers = {'Authorization': f'Basic {base64_message}'}
        res = post(url, headers=headers, data=data)
        if res.status_code != 200:
            return False, res

        res = json_loads(res.text)
        # access_token
        # token_type
        # expires_in

        return True, res

    def set_service_token(self):
        success, token_req = self.create_service_token()
        if success:
            self.oath_headers = {'Authorization': f'{token_req["token_type"]} {token_req["access_token"]}'}
            self.token_expiration_time = datetime.now() + timedelta(seconds=int(token_req["expires_in"]))
            self.server_usage = True
        return success, token_req

    def check_token(self):
        if self.server_usage and self.token_expiration_time < datetime.now():
            return self.set_service_token()

    def create_token(self):
        spotify_redirect()

    def get_requests(self, url, params={}):
        self.check_token()
        result = {}
        if params:
            # replace spaces with 20%
            params = urlencode(params, quote_via=quote)
            res = get(url, headers=self.oath_headers, params=params)
        else:
            res = get(url, headers=self.oath_headers)

        success = res.status_code == 200
        if success:
            result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}

    def post_requests(self, url, data):
        self.check_token()
        result = {}
        res = post(url, headers=self.oath_headers, json=data)
        success = res.status_code in (200, 201)
        if success:
            result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}

    def put_requests(self, url, data):
        self.check_token()
        result = {}
        res = put(url, headers=self.oath_headers, json=data)
        success = res.status_code in (200, 201)
        if success:
            result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}

    def find_track(self, track_name):
        artist, title = track_name.split('-')
        params = {
                    'q': f'artist:{artist.strip()} track:{title.strip()}',
                    'type': 'track',
                    'limit': '1'
                 }
        res = self.get_requests(f'{self.api_url}search', params)

        if res['success'] and len(res['result']['tracks']['items']) > 0:
            res = res['result']['tracks']['items'][0]
            res = {'artist': res['artists'][0]['name'], 'name': res['name'], 'id': res['id'], 'uri': res['uri'],
                   'type': res['type']}
        else:
            res = {}
        return res


    def get_user_info(self):
        res = self.get_requests(self.api_url + 'me')
        if res['success']:
            res['result'] = {
                # 'country': res.get('country'),
                'display_name': res['result'].get('display_name'),
                'id': res['result'].get('id'),
                'uri': res['result'].get('uri')
            }
        return res

    def get_user_playlists(self):
        limit = SpotifyConfig.PLAYLISTS_REQUEST_LIMIT
        offset = 0
        all_playlists = []
        url = self.api_url + 'me/playlists'

        params = {'offset': offset,
                  'limit': limit}

        res = self.get_requests(url, params)
        if not res['success']:
            return res

        res = res['result'].get('items', [])

        all_playlists += res

        while len(res) == limit:
            params['offset'] += limit
            res = self.get_requests(url, params)
            if not res['success']:
                return res
            all_playlists += res['result'].get('items', [])

        res = [
                    {
                        'name': playlist['name'],
                        'description': playlist['description'],
                        'tracks_total': playlist['tracks']['total'],
                        'id': playlist['id'],
                        'uri': playlist['uri']
                     } for playlist in all_playlists
                ]

        return {'success': True, 'result': res}

    def get_user_radios_playlists(self):
        res = []
        playlists = self.get_user_playlists()
        if not playlists['success']:
            return playlists

        for playlist in playlists['result']:
            if playlist['description'] == SpotifyConfig.DEFAULT_PLAYLIST_DESCRIPTION:
                res.append(playlist)

        return {'success': True, 'result': res}