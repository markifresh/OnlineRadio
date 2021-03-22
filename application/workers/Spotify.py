import requests
from json import loads as json_loads
from urllib.parse import urlencode, quote
from config import SpotifyConfig as config_spotify
from base64 import b64encode
import concurrent.futures
from time import sleep



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


        success = res.status_code == 200
        result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}

    def post_requests(self, url, data):
        res = requests.post(url, headers=self.oath_headers, json=data)
        success = res.status_code in (200, 201)
        result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}

    def put_requests(self, url, data):
        res = requests.put(url, headers=self.oath_headers, json=data)
        success = res.status_code in (200, 201)
        result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}


    def refresh_token(self, refresh_token):
        url = self.main_url + 'refresh'
        data = {'refresh_token': refresh_token}
        return self.post_requests(url, data)

    def get_user_data(self):
        res = self.get_requests(self.main_url + 'me')
        if res['success']:
            res['result'] = {
                # 'country': res.get('country'),
                'display_name': res['result'].get('display_name'),
                'id': res['result'].get('id'),
                'uri': res['result'].get('uri')
            }
        return res

    def set_user_id(self):
        if not self.user_id:
            res = self.get_user_data()
            if res['success']:
                self.user_id = res['result'].get('id', '')
        return self.user_id


    def get_user_playlists(self):
        limit = self.playlists_request_limit
        offset = 0
        all_playlists = []
        url = self.main_url + 'me/playlists'

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

    def get_radios_playlists(self):
        res = []
        playlists = self.get_user_playlists()
        if not playlists['success']:
            return playlists

        for playlist in playlists['result']:
            if playlist['description'] == self.default_playlist_description:
                res.append(playlist)

        return {'success': True, 'result': res}


    def set_user_playlists(self):
        user_playlists = self.get_user_playlists()
        if user_playlists['success']:
            self.playlists = user_playlists['result']
        return self.playlists

    def get_user_playlist_by_name(self, name):
        playlists = self.get_user_playlists()

        if not playlists['success']:
            return {'success': False, 'result': 'no playlists at all'}

        name = name.lower()
        for playlist in playlists['result']:
            if playlist['name'].lower() == name:
                return {'success': True, 'result': playlist}

        return {'success': False, 'result': 'playlist not found'}

    def get_user_playlist_by_id(self, playlist_id):
        result = {'playlist': {}, 'tracks': []}
        url = self.main_url + f'playlists/{playlist_id}'
        params = {'fields': 'name,id,uri,tracks.total'}

        # if with_tracks:
        #     params['fields'] += ',tracks.items(added_at,track.artists.name,track.name,track.album(name,release_date))'

        res = self.get_requests(url, params)

        if not res['success']:
            return res

        playlist = res['result']
        # if with_tracks:
        #     result['tracks'] = [
        #         {'added_at': track['added_at'],
        #          'artist': track['track']['artists'][0]['name'],
        #          'title': track['track']['name'],
        #          'album': track['track']['album']['name'],
        #          'album_date': track['track']['album']['release_date']} for track in playlist['tracks']['items']]
        result['playlist'] = {
                                'name': playlist['name'],
                                'id': playlist['id'],
                                'tracks_num': playlist['tracks']['total'],
                                'uri': playlist['uri']
                            }
        res['result'] = result
        return res
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

        res = self.get_requests(url, params)
        if not res['success']:
            return res

        raw_tracks += res['result'].get('items', [])

        while len(res) == limit:
            params['offset'] += limit
            res = self.get_requests(url, params)
            if not res['success']:
                return res

            raw_tracks += res['result'].get('items', [])

        if raw_tracks:
            tracks = [
                        {'added_at': track['added_at'],
                         'artist': track['track']['artists'][0]['name'],
                         'title': track['track']['name'],
                         'album': track['track']['album']['name'],
                         'album_date': track['track']['album']['release_date']} for track in raw_tracks]

        return {'success': True, 'result': tracks}


    def add_uris_to_playlist(self, playlist, tracks_uris):
        playlist = playlist if isinstance(playlist, str) else playlist.get('id', '')
        tracks_uris = tracks_uris if isinstance(tracks_uris, list) else [tracks_uris]
        res = self.post_requests(f'{self.main_url}playlists/{playlist}/tracks', {"uris": tracks_uris})

        if not res['success'] and res['headers'].get('retry-after'):
            while res['headers'].get('retry-after'):
                sleep(int(res['headers'].get('retry-after')))
                res = self.post_requests(f'{self.main_url}playlists/{playlist}/tracks', {"uris": tracks_uris})

        return res

    def add_tracks_to_playlist(self, playlist_name, tracks):
        final_result = []
        if isinstance(playlist_name, str):
            playlist = self.get_user_playlist_by_name(playlist_name)
            # playlist = self.create_user_playlist(name=playlist_name)

        if not playlist['success']:
            return playlist

        playlist_id = playlist['result'].get('id')
        tracks = [tracks] if not isinstance(tracks, list) else tracks
        failed_to_find = []
        errored = []
        to_add = []
        added = []
        result = {
            'success': False,
            'result': '',
            'failed': failed_to_find,
            'added': added,
            'playlist_id': playlist_id
        }

        tracks = self.find_tracks(tracks)
        for track in tracks:
            common_name = track['common_name']
            if track['success']:
                # to_add.append(track['result']['uri'])
                added.append({'common_name': common_name,
                              'in_spotify': track['result']['uri'],
                              'album_name': track['result']['album_name'],
                              'album_year': track['result']['album_year']})

            else:
                if track['error']:
                    errored.append(track)
                else:
                    failed_to_find.append(common_name)

        print('total to add: ' + str(len(added)))
        max_limit = config_spotify.TRACKS_ADD_LIMIT
        if len(added) > max_limit:

            current_id = 0
            till_id = max_limit

            while till_id < len(added):
                print(current_id, till_id)
                cur_added = added[current_id:till_id]
                to_add = [track['in_spotify'] for track in cur_added]
                res = self.add_uris_to_playlist(playlist_id, to_add)
                res['added'] = cur_added
                final_result.append(res)
                current_id += max_limit

                if len(added[current_id:-1]) + 1 > max_limit:
                    till_id = current_id + max_limit

                else:
                    till_id = len(added)
                    cur_added = added[current_id:till_id]
                    to_add = [track['in_spotify'] for track in cur_added]
                    res = self.add_uris_to_playlist(playlist_id, to_add)
                    res['added'] = cur_added
                    final_result.append(res)
                    print(current_id, till_id)
                    break

        else:
            to_add = [track['in_spotify'] for track in added]
            res = self.add_uris_to_playlist(playlist_id, to_add)
            res['added'] = added
            final_result.append(res)

        res = {
                'success': True,
                'result': final_result,
                'failed_to_find': failed_to_find,
                'errored': errored
              }

        return res


    def create_user_playlist(self, name, description=''):
        description = self.default_playlist_description if not description else description
        user_id = self.set_user_id()
        if not user_id:
            return {'success': False, 'result': 'Failed to get user ID'}

        data = {
                  "name": name,
                  "description": description,
                  "public": False
                }
        return self.post_requests(f'{self.main_url}users/{user_id}/playlists', data)

    def change_user_playlist(self, playlist_id, name='', description='', public=''):
        url = f'{self.main_url}playlists/{playlist_id}'
        data = {}

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if public:
            data['public'] = public

        return self.put_requests(url, data)

    # client_id = 'CLIENT_ID'
    # client_secret = 'CLIENT_SECRET'
    # redirect_url = 'REDIRECT_URI'
    # scopes = 'playlist-modify-public playlist-modify-private playlist-read-private'

    def find_track(self, track_name):
        if isinstance(track_name, dict):
            artist, title = track_name['artist'], track_name['title']

        elif isinstance(track_name, str) and '-' in track_name:
            artist, title = track_name.split('-')

        else:
            return {'success': False, 'error': True, 'result': 'Incorrect track name format', 'common_name': track_name}

        common_name = f'{artist} - {title}'
        params = {
                    'q': f'artist:{artist.strip()} track:{title.strip()}',
                    'type': 'track',
                    'limit': '1'
                 }
        res = self.get_requests(f'{self.main_url}search', params)

        if not res['success'] and res['headers'].get('retry-after'):
            while res['headers'].get('retry-after'):
                sleep(int(res['headers'].get('retry-after')))
                res = self.get_requests(f'{self.main_url}search', params)

        if not res['success']:
            res['error'] = True
            res['common_name'] = common_name
            return res

        res['common_name'] = common_name
        res['error'] = False

        if res['result'] and len(res['result']['tracks']['items']) > 0:
            result = res['result']['tracks']['items'][0]
            result = {
                    'artist': result['artists'][0]['name'],
                    'name': result['name'],
                    'id': result['id'],
                    'uri': result['uri'],
                    # 'popularity': result['popularity'],
                    # 'duration':result['duration_ms'],
                    'type': result['type'],
                    'album_year': result['album']['release_date'].split('-')[0],
                    'album_name': result['album']['name']}
            res['result'] = result

        else:
            res['success'] = False

        return res


    def find_tracks(self, tracks_list):
        result = []

        def run_search_tracks(track_list):
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                future = executor.map(self.find_track, track_list)
                for res in future:
                    result.append(res)

        max_limit = config_spotify.TRACKS_SEARCH_LIMIT
        if len(tracks_list) > max_limit:
            current_id = 0
            till_id = max_limit

            while till_id < len(tracks_list):
                print(current_id, till_id)
                run_search_tracks(tracks_list[current_id:till_id])
                current_id += max_limit

                if len(tracks_list[current_id:-1]) + 1 > max_limit:
                    till_id = current_id + max_limit

                else:
                    till_id = len(tracks_list)
                    run_search_tracks(tracks_list[current_id:till_id])
                    print(current_id, till_id)
                    break

        else:
            run_search_tracks(tracks_list)

        return result


    # without getting to user info (playlists and etc)
    def simple_auth(self):
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

    def refresh_token(self, refresh_token):
        message = config_spotify.CLIENT_ID + ':' + config_spotify.CLIENT_KEY
        message_bytes = message.encode('ascii')
        base64_bytes = b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        url = config_spotify.SPOTIFY_TOKEN_URL
        data = {'grant_type': 'refresh_token',
                'refresh_token': refresh_token}
        headers = {'Authorization': f'Basic {base64_message}'}
        res = requests.post(url, headers=headers, data=data)
        if res.status_code == 200:
            return json_loads(res.text)
        return {}
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