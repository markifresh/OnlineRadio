import requests
from json import loads as json_loads
from urllib.parse import urlencode, quote
from config import SpotifyConfig as config_spotify



class SpotifyAPI:
    def __init__(self, oath_token='', oauth_type=''):
        self.default_playlist_description = 'playlist for radio_app'
        self.oath_token = oath_token
        self.oauth_type = oauth_type
        self.oath_headers = {'Authorization': f'{oauth_type} {oath_token}'}
        self.main_url = f'{config_spotify.SPOTIFY_API_BASE_URL}/{config_spotify.SPOTIFY_API_VERSION}/'
        self.user_id = ''
        self.playlists = []
        self.headers = {}
        self.playlists_request_limit = config_spotify.PLAYLISTS_REQUEST_LIMIT
        self.playlist_tracks_request_limit = config_spotify.PLAYLIST_TRACKS_REQUEST_LIMIT

    def set_initial_data(self):
        self.set_user_id()
        self.set_user_playlists()

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
        if not self.user_id:
            self.user_id = self.get_requests(self.main_url + 'me').get('id', '')
        return self.user_id

    def get_user_data(self):
        res = self.get_requests(self.main_url + 'me')
        if res:
            res = {
                # 'country': res.get('country'),
                'display_name': res.get('display_name'),
                'id': res.get('id'),
                'uri': res.get('uri')
            }
        return res


    def get_user_playlists(self):
        limit = self.playlists_request_limit
        offset = 0
        all_lists = []
        url = self.main_url + 'me/playlists'

        params = {'offset': offset,
                  'limit': limit}

        res = self.get_requests(url, params).get('items', [])
        all_lists += res

        while len(res) == limit:
            params['offset'] += limit
            res = self.get_requests(url, params).get('items', [])
            all_lists += res

        return all_lists

    def get_radios_playlists(self):
        res = []
        playlists = self.get_user_playlists()
        for playlist in playlists:
            print(playlist['description'])
            if playlist['description'] == self.default_playlist_description:
                res.append(
                    {'name': playlist['name'],
                     'href': playlist['href'],
                     'id': playlist['id'],
                     'tracks_num': playlist['tracks']['total'],
                     'uri': playlist['uri']
                     }
                )
        return res


    def set_user_playlists(self):
        self.playlists = self.get_user_playlists()
        return self.playlists

    def get_user_playlist_by_name(self, name):
        playlists = self.playlists if self.playlists else self.set_user_playlists()

        name = name.lower()
        for playlist in playlists:
            if playlist['name'].lower() == name:
                return playlist

        return {}

    def get_user_playlist_by_id(self, playlist_id, with_tracks=False):
        result = {'playlist': {}, 'tracks': []}
        url = self.main_url + f'playlists/{playlist_id}'
        params = {'fields': 'name,id,uri,tracks.total'}

        if with_tracks:
            params['fields'] += ',tracks.items(added_at,track.artists.name,track.name,track.album(name,release_date))'

        print(params)
        res = self.get_requests(url, params)
        print(res)
        if res:
            playlist = res
            if with_tracks:
                result['tracks'] = [
                    {'added_at': track['added_at'],
                     'artist': track['track']['artists'][0]['name'],
                     'title': track['track']['name'],
                     'album': track['track']['album']['name'],
                     'album_date': track['track']['album']['release_date']} for track in playlist['tracks']['items']]

            result['playlist'] = {
                                    'name': playlist['name'],
                                    'id': playlist['id'],
                                    'tracks_num': playlist['tracks']['total'],
                                    'uri': playlist['uri']
                                }
        return result
    # maximum 100 tracks per request
    # maximum 10 000 tracks in playlist
    # playlist['tracks']['total'] < len(tracks_to_add)

    def get_playlist_tracks(self, playlist_id):
        raw_tracks = []
        tracks = []
        limit = self.playlist_tracks_request_limit
        offset = 0
        url = self.main_url + f'playlists/{playlist_id}/tracks'

        params = {'offset': offset,
                  'limit': limit,
                  'fields': 'items(added_at,track.artists.name,track.name),items.track.album(name,release_date)'}

        res = self.get_requests(url, params).get('items', [])
        raw_tracks += res

        while len(res) == limit:
            params['offset'] += limit
            res = self.get_requests(url, params).get('items', [])
            raw_tracks += res

        if raw_tracks:
            tracks = [
                        {'added_at': track['added_at'],
                         'artist': track['track']['artists'][0]['name'],
                         'title': track['track']['name'],
                         'album': track['track']['album']['name'],
                         'album_date': track['track']['album']['release_date']} for track in raw_tracks]
        return tracks


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
        description = self.default_playlist_description if not description else description
        data = {
                  "name": name,
                  "description": description,
                  "public": False
                }
        return self.post_requests(f'{self.main_url}users/{self.set_user_id()}/playlists', data)

    # client_id = 'CLIENT_ID'
    # client_secret = 'CLIENT_SECRET'
    # redirect_url = 'REDIRECT_URI'
    # scopes = 'playlist-modify-public playlist-modify-private playlist-read-private'

    def find_track(self, track_name):
        artist, title = track_name.split('-')
        params = {
                    'q': f'artist:{artist.strip()} track:{title.strip()}',
                    'type': 'track',
                    'limit': '1'
                 }
        res = self.get_requests(f'{self.main_url}search', params)

        if res and len(res['tracks']['items']) > 0:
            res = res['tracks']['items'][0]
            res = {'artist': res['artists'][0]['name'], 'name': res['name'], 'id': res['id'], 'uri': res['uri'],
                   'type': res['type']}
        else:
            res = {}
        return res


    # without getting to user info (playlists and etc)
    def simple_auth(self):
        from base64 import b64encode
        message = config_spotify.CLIENT_ID + ':' + config_spotify.CLIENT_KEY
        message_bytes = message.encode('ascii')
        base64_bytes = b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        url = config_spotify.SPOTIFY_TOKEN_URL
        data = {'grant_type': 'client_credentials'}
        headers = {'Authorization': f'Basic {base64_message}'}
        res = requests.post(url, headers=headers, data=data)
        if res.status_code == 200:
            res = json_loads(res.text)
            token = res['access_token']
            token_type = res['token_type']
            self.oath_headers = {'Authorization': f'{token_type} {token}'}

        return len(self.oath_headers) > 0


        # url = 'https://api.spotify.com/v1/tracks/2TpxZ7JUBn3uw46aR7qd6V'
        # headers = {'Authorization': f'{token_type} {token}'}
        # res = requests.get(url, headers=headers)
        #
        # import spotipy
        # from spotipy.oauth2 import SpotifyOAuth
        # scope = "user-library-read"
        # sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    def with_flask(self):
        provider_url = config_spotify.SPOTIFY_AUTH_URL
        params = urlencode({
            'client_id': config_spotify.CLIENT_ID,
            'scope': ['user-read-email', 'user-follow-read'],
            'redirect_uri': 'http://127.0.0.1:5000/spotify/callback',
            'response_type': 'code'
        })

        url = provider_url + '?' + params
        requests.get(url)