from application.music_services.MSAbstract import MSAbstract
from config import DeezerConfig
from application.pages.oauth_page import deezer_redirect
from requests import get, post, delete
from urllib.parse import urlencode, quote
from json import loads as json_loads


class DeezerService(MSAbstract):
    api_url = DeezerConfig.DEEZER_API_BASE_URL
    tracks_search_limit = DeezerConfig.TRACKS_ADD_LIMIT

    def create_token(self):
        deezer_redirect()

    def get_requests(self, url, params={}):
        url = self.api_url + url

        if self.token:
            params['access_token'] = self.token

        if params:
            res = get(url, params=params)

        else:
            res = get(url)

        success = res.status_code == 200
        result = json_loads(res.text)

        return {'success': success, 'result': result, 'headers': dict(res.headers)}

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
                            'name': user['name'],
                            'firstname': user['firstname'],
                            'lastname': user['lastname'],
                        }

        return res

    def get_user_playlists(self):
        res = self.get_requests('/user/me/playlists')
        if not res['success']:
            return res

        user = res['result']
        result = {
                    'id': user['id'],
                    'name': user['name'],
                    'firstname': user['firstname'],
                    'lastname': user['lastname'],
                  }

        return {'success': True, 'result': result}
