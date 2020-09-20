import requests
import secret_data
from json import loads as json_loads
from urllib.parse import urlencode, quote




class SpotifyAPI:
    def __init__(self, oath_token):
        self.oath_token = oath_token
        self.oath_headers = {'Authorization': f'Bearer {oath_token}'}
        self.main_url = 'https://api.spotify.com/v1/'
        self.user_id = ''
        self.playlists = []
        pass

    def get_requests(self, url, params={}):
        if params:
            # replace spaces with 20%
            params = urlencode(params, quote_via=quote)
            res = requests.get(url, headers=self.oath_headers, params=params)
        else:
            res = requests.get(url, headers=self.oath_headers)

        if res.status_code == 200:
            return json_loads(res.text)
        return {}

    def post_requests(self, url, data):
        res = requests.post(url, headers=self.oath_headers, json=data)
        if res.status_code in (200, 201):
            return json_loads(res.text)
        return {}

    def set_user_id(self):
        self.user_id = self.get_requests(self.main_url + 'me').get('id', '')
        return self.user_id

    def get_user_playlists(self):
        return self.get_requests(self.main_url + 'me/playlists').get('items', [])

    def set_user_playlists(self):
        self.playlists = self.get_user_playlists()
        return self.playlists

    def get_user_playlist_by_name(self, name):
        playlists = self.playlists if self.playlists else self.get_user_playlists()

        if not playlists:
            return {}

        name = name.lower()
        for playlist in playlists:
            if playlist['name'].lower() == name:
                return playlist

        return {}

    # maximum 100 tracks per request
    # maximum 10 000 tracks in playlist
    # playlist['tracks']['total'] < len(tracks_to_add)
    def add_tracks_to_playlist(self, playlist, tracks):
        playlist = playlist if isinstance(playlist, str) else playlist.get('id', '')
        tracks = tracks if isinstance(tracks, list) else [tracks]
        if not playlist and len(tracks) > 100:
            return {}
        uris = []
        for track in tracks:
            uris.append('spotify:track:' + track)
        return self.post_requests(f'{self.main_url}playlists/{playlist}/tracks', {"uris": uris})


    def create_user_playlist(self, name, description=''):
        data = {
                  "name": name,
                  "description": description,
                  "public": False
                }
        return self.post_requests(f'{self.main_url}users/{self.user_id}/playlists', data)

    client_id = 'CLIENT_ID'
    client_secret = 'CLIENT_SECRET'
    redirect_url = 'REDIRECT_URI'
    scopes = 'playlist-modify-public playlist-modify-private playlist-read-private'

    def find_track(self, track_name):
        artist, title = track_name.split('-')
        params = {
                    'q': f'artist:{artist.strip()} track:{title.strip()}',
                    'type': 'track',
                    'limit': '1'
                 }
        res = self.get_requests(f'{self.main_url}search', params)

        if len(res['tracks']['items']) > 0:
            res = res['tracks']['items'][0]
            res = {'artist': res['artists'][0]['name'], 'name': res['name'], 'id': res['id'], 'uri': res['uri'],
                   'type': res['type']}
        else:
            res = {}
        return res


    # without getting to user info (playlists and etc)
    def simple_auth(self):
        from base64 import b64encode
        message = secret_data.spotify_api_id + ':' + secret_data.spotify_api_key
        message_bytes = message.encode('ascii')
        base64_bytes = b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        url = 'https://accounts.spotify.com/api/token'
        data = {'grant_type': 'client_credentials'}
        headers = {'Authorization': f'Basic {base64_message}'}
        res = requests.post(url, headers=headers, data=data)
        if res.status_code == 200:
            res = json_loads(res.text)
            token = res['access_token']
            token_type = res['token_type']

        url = 'https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aR7qd6V'
        headers = {'Authorization': f'{token_type} {token}'}
        res = requests.get(url, headers=headers)

        import spotipy
        from spotipy.oauth2 import SpotifyOAuth
        scope = "user-library-read"
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    def with_flask(self):
        provider_url = "https://accounts.spotify.com/authorize"
        params = urlencode({
            'client_id': secret_data.spotify_api_id,
            'scope': ['user-read-email', 'user-follow-read'],
            'redirect_uri': 'http://127.0.0.1:5000/spotify/callback',
            'response_type': 'code'
        })

        url = provider_url + '?' + params
        requests.get(url)