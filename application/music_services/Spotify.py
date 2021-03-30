from application.music_services.MSAbstract import MSAbstract
from urllib.parse import quote, urlencode
from config import SpotifyConfig
from requests import get, post, put
from json import loads as json_loads
from base64 import b64encode
from datetime import datetime, timedelta
from time import sleep
from concurrent.futures import ThreadPoolExecutor

class Spotify(MSAbstract):
    api_url = SpotifyConfig.SPOTIFY_API_URL
    tracks_search_limit = SpotifyConfig.TRACKS_SEARCH_LIMIT
    playlist_tracks_request_limit = SpotifyConfig.PLAYLISTS_REQUEST_LIMIT
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

    # def create_token(self):
    #     spotify_redirect()

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

    # def find_track(self, track_name):
    #     artist, title = track_name.split('-')
    #     params = {
    #                 'q': f'artist:{artist.strip()} track:{title.strip()}',
    #                 'type': 'track',
    #                 'limit': '1'
    #              }
    #     res = self.get_requests(f'{self.api_url}search', params)
    #
    #     if res['success'] and len(res['result']['tracks']['items']) > 0:
    #         res = res['result']['tracks']['items'][0]
    #         res = {'artist': res['artists'][0]['name'], 'name': res['name'], 'id': res['id'], 'uri': res['uri'],
    #                'type': res['type']}
    #     else:
    #         res['success'] = False
    #
    #     return res


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
        url = self.api_url + f'playlists/{playlist_id}'
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

    def get_playlist_tracks(self, playlist_id):
        raw_tracks = []
        tracks = []
        limit = self.playlist_tracks_request_limit
        offset = 0
        url = self.api_url + f'playlists/{playlist_id}/tracks'

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
        res = self.get_requests(f'{self.api_url}search', params)

        if not res['success'] and res['headers'].get('retry-after'):
            while res['headers'].get('retry-after'):
                sleep(int(res['headers'].get('retry-after')))
                res = self.get_requests(f'{self.api_url}search', params)

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

    def add_uris_to_playlist(self, playlist, tracks_uris):
        playlist = playlist if isinstance(playlist, str) else playlist.get('id', '')
        tracks_uris = tracks_uris if isinstance(tracks_uris, list) else [tracks_uris]
        res = self.post_requests(f'{self.api_url}playlists/{playlist}/tracks', {"uris": tracks_uris})

        if not res['success'] and res['headers'].get('retry-after'):
            while res['headers'].get('retry-after'):
                sleep(int(res['headers'].get('retry-after')))
                res = self.post_requests(f'{self.api_url}playlists/{playlist}/tracks', {"uris": tracks_uris})

        return res

    def add_track_to_playlist(self, playlist_name, track):
        return self.add_tracks_to_playlist(playlist_name, [track])


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
        max_limit = SpotifyConfig.TRACKS_ADD_LIMIT
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


    def create_user_playlist(self, name, description='', user_id=''):
        user_id = user_id['id'] if isinstance(user_id, dict) else user_id
        if not user_id:
            res = self.get_user_info()
            if not res['success']:
                return res

            user_id = res['result']['id']

        description = SpotifyConfig.DEFAULT_PLAYLIST_DESCRIPTION if not description else description

        data = {
                  "name": name,
                  "description": description,
                  "public": False
                }

        return self.post_requests(f'{self.api_url}users/{user_id}/playlists', data)

    def change_user_playlist(self, playlist_id, name='', description='', public=''):
        url = f'{self.api_url}playlists/{playlist_id}'
        data = {}

        if name:
            data['name'] = name

        if description:
            data['description'] = description

        if public:
            data['public'] = public

        return self.put_requests(url, data)

    def find_tracks(self, tracks_list):
        result = []

        def run_search_tracks(track_list):
            with ThreadPoolExecutor(max_workers=20) as executor:
                future = executor.map(self.find_track, track_list)
                for res in future:
                    result.append(res)

        max_limit = self.tracks_search_limit
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