from application.radios.RadioAbstract import RadioAbstract
from datetime import datetime, timedelta, date
from requests import post as req_post
from json import loads as json_loads
from concurrent.futures import ThreadPoolExecutor
from application.workers.ExtraFunc import sort_tracks_list
from config import APIConfig


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
        super().__init__(radio_id)

    @classmethod
    def get_stations(cls):
        json = {'query': '{ brand'
        f'(id: {cls.parent_id}) '
                         '{ id  liveStream webRadios { id liveStream description} } } '}
        headers = {'x-token': APIConfig.radiofrance_api_key}
        res = req_post(url=cls.tracks_request_url, json=json, headers=headers)

        if res.status_code != 200:
            return {'success': False, 'result': res.status_code, 'respond': res.text}
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

        return {'success': True, 'result': fip_stations, 'respond': ''}

    @classmethod
    def get_radios(cls):
        result = []
        stations = cls.get_stations()
        if stations['success']:
            result = stations['result']
        return {'success': len(result) > 0, 'result': result}

    def get_radio_tracks(self, play_date):
        request_time = datetime.now()

        if isinstance(play_date, str) and '-' in play_date:
            orig_date = play_date
            day, month, year = play_date.split('-')[:3]             #06/09/2020
            day, month, year = int(day), int(month), int(year)
            play_date = datetime(year=year, month=month, day=day)
            orig_date = orig_date.replace('-', '/')

        elif isinstance(play_date, (datetime, date)):
            orig_date = play_date.strftime('%d/%m/%Y')
            day = play_date.day
            play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)

        else:
            return {'success': False, 'result': 'incorrect date format', 'respond': ''}

        from_date = play_date
        responds_list = []
        res_list = []
        dates_list = []
        dates_list.append(from_date)
        time_step = 4
        from_date += timedelta(hours=time_step)

        while from_date.day == day:
            dates_list.append(from_date)
            from_date += timedelta(hours=time_step)

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
                'for_date': play_date, 'request_time': request_time}

    def get_current_track(self):
        orig_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        url = self.tracks_request_url
        json = {'query': '{ live'
                         f'(station: {self.radio_id}) '
                         '{ song { start end track  { mainArtists title  } } } }  '}

        headers = {'x-token': APIConfig.radiofrance_api_key}
        res = req_post(url=url, json=json, headers=headers)

        if res.status_code != 200:
            return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}

        track = json_loads(res.text)['data']['live']['song']
        play_time = track.get('start', '')

        if not play_time:
            start_date = orig_date
        else:
            start_date = datetime.fromtimestamp(play_time).strftime('%d/%m/%Y %H:%M:%S')

        end_time = track.get('end', '')

        if not end_time:
            end_date = orig_date
        else:
            end_date = datetime.fromtimestamp(end_time).strftime('%d/%m/%Y %H:%M:%S')

        track = track['track']
        if track:
            artist = ','.join(track.get('mainArtists', '')).strip()
            title = track.get('title', '').strip()
            common_name = f'{artist} - {title}'
            return {'album_name': track.get('albumTitle', ''),
                    'common_name': common_name,
                    'artist': artist,
                    'title': title,
                    'start_date': start_date,
                    'end_date': end_date,
                    'radio_name': self.radio_id}

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