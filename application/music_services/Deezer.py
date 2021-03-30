from application.music_services.MSAbstract import MSAbstract
from config import DeezerConfig
# from application.pages.oauth_page import deezer_redirect
from requests import get, post, delete
from urllib.parse import urlencode, quote
from json import loads as json_loads
from datetime import datetime, timedelta


class Deezer(MSAbstract):
    api_url = DeezerConfig.DEEZER_API_BASE_URL
    tracks_search_limit = DeezerConfig.TRACKS_ADD_LIMIT

    # def create_token(self):
    #     deezer_redirect()

    def __init__(self, token='', expires_in_sec=0):
        self.token = token
        self.token_expiration_time = datetime.now() + timedelta(seconds=int(expires_in_sec))

    def make_request(self, method, url, params={}, data={}):
        url = self.api_url + url

        if self.token:
            params['access_token'] = self.token

        if not params:
            res = method(url, json=data)

        else:
            res = method(url, params=params, json=data)

        success = res.status_code == 200 and 'Exception' not in res.text
        result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}

    def get_requests(self, url, params={}, data={}):
        return self.make_request(method=get, url=url, params=params)

    def post_requests(self, url, params={}, data={}):
        return self.make_request(method=post, url=url, params=params)

    def delete_requests(self, url, params={}, data={}):
        return self.make_request(method=delete, url=url, params=params)

    def find_track(self, common_name):
        common_name = common_name.lower()
        final_result = {}
        artist, track = common_name.split('-')
        params = {
            #'q': common_name,
            'q': f'artist:"{artist}" track:"{track}"',
            'order': 'RANKING',
            'output': 'json'
        }
        res = self.get_requests('/search/track', params)
        if not res['success'] or len(res['result']['data']) == 0:
            return {'success': False, 'result': res['result']}

        #
        # for result in res['result']['data']:
        #     if result['']

        return {'success': True, 'result': res['result']['data'][0]}

    def get_user_info(self):
        res = self.get_requests('/user/me')
        if not res['success']:
            return res

        user = res['result']
        res['result'] = {
                            'id': user['id'],
                            'display_name': user['name'],
                            'uri': f'{DeezerConfig.DEEZER_URL}/profile/{user["id"]}',
                            'firstname': user['firstname'],
                            'lastname': user['lastname'],
                        }

        return res

    def get_user_playlists(self):
        res = self.get_requests('/user/me/playlists')
        if not res['success']:
            return res

        playlists = res['result']['data']
        return {'success': True, 'result': playlists}

    def get_user_playlist_by_name(self, playlist_name):
        playlists = self.get_user_playlists()
        if not playlists['success']:
            return playlists

        result = {'success': True, 'result': {}}
        playlist_name = playlist_name.lower()
        playlists = playlists['result']
        for playlist in playlists:
            if playlist['title'].lower() == playlist_name:
                result['result'] = playlist
                return result

        return result

    def get_user_radios_playlists(self):
        playlists = self.get_user_playlists()
        if not playlists['success']:
            return playlists

        radios_playlists = []
        from application.db_models.radio_db import Radio
        app_playlists = [DeezerConfig.DEFAULT_PLAYLIST_NAME + radio for radio in Radio.get_all_radios()]

        playlists = playlists['result']
        for playlist in playlists:
            if playlist["title"] in app_playlists:
                radios_playlists.append(playlist)

        return {'success': True, 'result': radios_playlists}

    def get_playlist_tracks(self, playlist_id):
        playlist_id_original = playlist_id
        playlist_id = playlist_id.get('id', '') if isinstance(playlist_id, dict) else playlist_id
        if not playlist_id:
            return {'success': False, 'result': f'id not found in: {playlist_id_original}'}

        res = self.get_requests(f'/playlist/{playlist_id}/tracks')

        if res['success']:
            res['result'] = res['result']['data']

        return res

    # todo: rewrite correct and test
    def sort_playlist(self, playlist_id):
        playlist_id_original = playlist_id
        playlist_id = playlist_id.get('id', '') if isinstance(playlist_id, dict) else playlist_id
        if not playlist_id:
            return {'success': False, 'result': f'id not found in: {playlist_id_original}'}

        tracks = self.get_playlist_tracks(playlist_id)
        if not tracks['success']:
            return tracks

        tracks = tracks['result']
        tracks.sort(lambda x: x['rank'])
        tracks_order = [track['id'] for track in tracks]

        return self.post_requests(url=f'/playlist/{playlist_id}/tracks',
                                  data={'order': tracks_order})

    def create_playlist(self, name):
        return self.post_requests(url=f'/user/me/playlists',
                                  params={'title': name})

    def add_track_to_playlist(self, playlist_id, track_id):
        track_id_original = track_id
        track_id = track_id.get('id', '') if isinstance(track_id, dict) else track_id
        if not track_id:
            return {'success': False, 'result': f'id not found in: {track_id_original}'}

        playlist_id_original = playlist_id
        playlist_id = playlist_id.get('id', '') if isinstance(playlist_id, dict) else playlist_id
        if not playlist_id:
            return {'success': False, 'result': f'id not found in: {playlist_id_original}'}

        return self.post_requests(url=f'/playlist/{playlist_id}/tracks',
                                  params={'songs': track_id})

    # todo: rewrite correct and test
    def add_tracks_to_playlist(self, playlist_id, tracks_ids):
        if not isinstance(tracks_ids, list):
            return {'success': False, 'result': f'tracks id should be a list'}

        ids_to_add = ''
        for track in tracks_ids:
            if isinstance(track, dict):
                ids_to_add += track['id'] + ','
            else:
                return {'success': False, 'result': f'tracks should be of type dict'}

        return self.add_track_to_playlist(playlist_id, ids_to_add)
