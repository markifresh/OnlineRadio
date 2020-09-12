from requests import get
import secret_data
from json import loads as json_loads
from urllib.parse import urlencode, quote

class YouTubeAPI:
    def __init__(self):
        self.key = secret_data.youtube_api_key
        self.main_url = 'https://www.googleapis.com/youtube'
        self.api_version = 'v3'
        self.url = f'{self.main_url}/{self.api_version}/'

    def get_requests(self, url, params):
        params = urlencode(params, quote_via=quote)
        res = get(url, params=params)
        if res.status_code == 200:
            return json_loads(res.text)
        return {}

    def get_video_by_name(self, name):
        final_res = {}
        params = {
                    'part': 'snippet',
                    'q': name,
                    'maxResults': '1',
                    'key': self.key
                  }

        res = self.get_requests(f'{self.url}search', params)

        if len(res['items']) > 0:
            res = res['items'][0]
            final_res['name'] = res['snippet']['title']
            final_res['id'] = res['id']['videoId']
            final_res['link'] = 'https://www.youtube.com/watch?v=' + final_res['id']

        return final_res

        # if len(res['tracks']['items']) > 0:
        #     res = res['tracks']['items'][0]
        #     res = {'artist': res['artists'][0]['name'], 'name': res['name'], 'id': res['id'], 'uri': res['uri'],
        #            'type': res['type']}
        # else:
        #     res = {}
        # return res