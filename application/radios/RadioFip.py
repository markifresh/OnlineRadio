from application.radios.RadioAbstract import RadioAbstract
from datetime import datetime, timedelta, date
from requests import post as req_post
from json import loads as json_loads
from concurrent.futures import ThreadPoolExecutor
from application.workers.ExtraFunc import sort_tracks_list
from config import APIConfig
from application import get_data_range


class Fip(RadioAbstract):
    parent_id = 'FIP'
    exclude_radios = ['FIP_REGGAE', 'FIP_METAL']
    url = 'https://www.fip.fr/'
    tracks_request_url = 'https://openapi.radiofrance.fr/v1/graphql'
    stream_url = ''
    description = 'France radio'
    country = 'France'
    genre = 'pop,soul,jazz,rock'

    def __init__(self, radio_id):
        radios = self.get_radios()

        if not radios['success']:
            raise Exception(f'Failed to get radios: {radios["result"]}')

        radios = radios['result']
        if radio_id not in radios.keys():
            raise Exception(f'Can not find radio "{radio_id}" in list of stations: {list(radios.keys())}')

        radio = radios[radio_id]
        self.radio_id = radio_id
        self.stream_url = radio['stream_url']
        self.genre = radio['genre']
        self.description = radio['description']

    @classmethod
    def get_radios(cls):
        json = {'query': '{ brand'
        f'(id: {cls.parent_id}) '
                         '{ id  liveStream webRadios { id liveStream description} } } '}
        headers = {'x-token': APIConfig.radiofrance_api_key}
        res = req_post(url=cls.tracks_request_url, json=json, headers=headers)

        if res.status_code != 200:
            return {'success': False, 'result': res.text}

        radio_url = cls.url
        radio = json_loads(res.text)['data']['brand']
        radios = radio['webRadios']
        fip_radio = {'name': radio['id'],
                     'url': radio_url,
                     'stream_url': radio['liveStream'],
                     'description': cls.description,
                     'genre': cls.genre,
                     'country': cls.country}
        fip_stations = {}
        for radio in radios:
            fip_stations[radio['id']] = {'name': radio['id'],
                                         'url': radio_url,
                                         'stream_url': radio['liveStream'],
                                         'genre': radio['id'].split('_')[-1],
                                         'description': radio['description'],
                                         'country': cls.country}
        fip_stations[fip_radio['name']] = fip_radio

        for excluded_station in cls.exclude_radios:
            if excluded_station in fip_stations:
                del fip_stations[excluded_station]

        return {'success': len(fip_stations) > 0, 'result': fip_stations, 'respond': ''}


    def get_radio_tracks_per_range(self, start_date, end_date):
        request_time = datetime.now()
        start_date, end_date = get_data_range(start_date, end_date)

        start_original = start_date

        responds_list = []
        res_list = []
        dates_list = []
        dates_list.append(start_date)
        time_step = 4
        start_date += timedelta(hours=time_step)

        while start_date < end_date:
            dates_list.append(start_date)
            start_date += timedelta(hours=time_step)

        def get_tracks_by_threads(one_date):
            start_time = str(int(one_date.timestamp()))
            end_time = str(int((one_date + timedelta(hours=time_step)).timestamp()))

            genre = self.radio_id.split('_')[-1].lower()
            url = self.tracks_request_url
            json = {'query': '{ grid'
                             f'(start: {start_time}, end: {end_time}, station: {self.radio_id}) '
                             '{ ... on TrackStep { start track  { mainArtists title albumTitle } } } }  ' }
            headers = {'x-token': APIConfig.radiofrance_api_key}
            res = req_post(url=url, json=json, headers=headers)
            responds_list.append((res.status_code, res.text))
            if res.status_code != 200:
                return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}

            tracks = json_loads(res.text)['data']['grid']
            for track in tracks:
                play_time = track.get('start', '')
                track_play_date = datetime.fromtimestamp(play_time)

                track = track['track']
                if track:
                    artist = ','.join(track.get('mainArtists', '')).strip()
                    title = track.get('title', '').strip()
                    common_name = f'{artist} - {title}'
                    to_add = {'album_name': track.get('albumTitle', ''),
                                     'common_name': common_name,
                                     'artist': artist,
                                     'title': title,
                                     'play_date': track_play_date,
                                     'radio_name': self.radio_id,
                                     'genre': genre}
                    if to_add not in res_list:
                        res_list.append(to_add)

        with ThreadPoolExecutor(max_workers=15) as executor:
            executor.map(get_tracks_by_threads, dates_list)

        return {'success': True, 'result': sort_tracks_list(res_list), 'responds_list': responds_list, 'respond': '',
                'for_date': '', 'request_time': request_time, 'start_date': start_original, 'end_date': end_date,}

    def get_current_track(self):
        # orig_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        url = self.tracks_request_url
        json = {'query': '{ live'
                         f'(station: {self.radio_id}) '
                         '{ song { start end track  { mainArtists title  } } } }  '}

        headers = {'x-token': APIConfig.radiofrance_api_key}
        res = req_post(url=url, json=json, headers=headers)

        if res.status_code != 200:
            return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}

        track = json_loads(res.text)['data']['live']['song']

        start_time = track.get('start', '')
        start_date = datetime.fromtimestamp(start_time)

        end_time = track.get('end', '')
        end_date = datetime.fromtimestamp(end_time)

        timetoplay = (end_date - datetime.now()).seconds

        track = track['track']
        if track:
            artist = ','.join(track.get('mainArtists', '')).strip()
            title = track.get('title', '').strip()
            common_name = f'{artist} - {title}'
            return {'common_name': common_name,
                    'artist': artist,
                    'title': title,
                    'start_date': start_date,
                    'end_date': end_date,
                    'radio_name': self.radio_id,
                    'timetoplay': timetoplay,
                    'spotify': '',
                    'deezer': ''}

        return {}

    def get_latest_tracks(self):
        end_time = datetime.now()
        orig_date = end_time.strftime('%d-%m-%Y')
        start_time = end_time - timedelta(minutes=30)
        start_time = str(int(start_time.timestamp()))
        end_time = str(int(end_time.timestamp()))

        res_list = []
        genre = self.radio_id.split('_')[-1].lower()
        url = self.tracks_request_url
        json = {'query': '{ grid'
                         f'(start: {start_time}, end: {end_time}, station: {self.radio_id}) '
                         '{ ... on TrackStep { start track  { mainArtists title albumTitle } } } }  '}

        headers = {'x-token': APIConfig.radiofrance_api_key}
        res = req_post(url=url, json=json, headers=headers)

        if res.status_code != 200:
            return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}
        tracks = json_loads(res.text)['data']['grid']

        for track in tracks:
            play_time = track.get('start', '')
            if not play_time:
                play_date = orig_date
            else:
                play_date = datetime.fromtimestamp(play_time).strftime('%d/%m/%Y %H:%M:%S')
            track = track['track']
            if track:
                artist = ','.join(track.get('mainArtists', '')).strip()
                title = track.get('title', '').strip()
                common_name = f'{artist} - {title}'
                res_list.append({'album_name': track.get('albumTitle', ''),
                                 'common_name': common_name,
                                 'artist': artist,
                                 'title': title,
                                 'play_date': play_date,
                                 'radio_name': self.radio_id,
                                 'genre': genre})

        return {'success': True, 'result': res_list, 'respond': ''}