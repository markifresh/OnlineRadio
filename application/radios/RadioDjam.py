from application.radios.RadioAbstract import RadioAbstract
from requests import post as req_post
from json import loads as json_loads
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from application.workers.ExtraFunc import get_date_range_list, sort_tracks_list
from application import get_data_range

class Djam(RadioAbstract):
    radio_id = 'DJAM'
    url = 'https://www.djamradio.com'
    tracks_request_url = 'https://www.djamradio.com/actions/retrieve.php'
    stream_url = 'https://ledjamradio.ice.infomaniak.ch/ledjamradio.mp3'
    current_playing_url = 'https://www.djamradio.com/actions/infos.php'
    genre = 'jazz,soul,hiphop,pop'
    description = 'France radio'
    country = 'France'

    def __init__(self, radio_id=radio_id):
        super().__init__(radio_id)

    # as API of radio updates list of songs once in 40-60 mins, impossible to get tracks for latest hour
    # todo: if last hour in request, add to result output: get_latest_tracks
    def get_radio_tracks_per_range(self, start_date, end_date):
        request_time = datetime.now()
        start_date, end_date = get_data_range(start_date, end_date)

        start_original = start_date
        responds_list = []
        res_list = []
        dates_list = []
        dates_list.append(start_date)
        time_step_min = 30
        start_date += timedelta(minutes=time_step_min)

        while start_date < end_date:
            dates_list.append(start_date)
            start_date += timedelta(minutes=time_step_min)
        dates_list.append(start_date)

        def get_jam_tracks_threads(one_date):
            data = {'day': one_date.day, 'month': one_date.month, 'hour': one_date.hour, 'minute': one_date.minute}
            res = req_post(self.tracks_request_url, data=data)
            responds_list.append((res.status_code, res.text))
            elements = BeautifulSoup(res.text, 'html.parser').find_all('li')
            for li in elements:
                track_str = li.text
                if 'Cinema' not in track_str and 'Ledjam Radio' not in track_str and 'Television' not in track_str:
                    splited = track_str.split(' : ')
                    hours, minutes = splited[0].split('h')
                    track_play_date = datetime(day=one_date.day,
                                               month=one_date.month,
                                               year=one_date.year,
                                               hour=int(hours),
                                               minute=int(minutes))
                    common_name = ':'.join(splited[1:]).split('-')
                    title = common_name[0].strip()
                    artist = ('-'.join(common_name[1:])).strip()
                    common_name = f'{artist} - {title}'
                    to_add = {
                        'artist': artist,
                        'title': title,
                        'play_date': track_play_date,
                        'common_name': common_name,
                        'genre': 'djam'
                    }

                    if to_add not in res_list:
                        res_list.append(to_add)

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(get_jam_tracks_threads, dates_list)

        return {'success': True, 'result': sort_tracks_list(res_list), 'responds_list': responds_list, 'respond': '',
                'request_time': request_time, 'start_date': start_original, 'end_date': end_date, 'for_date': ''}


    def get_current_track(self):
        return self.get_latest_tracks()[0]

    def get_latest_tracks(self):
        """
        0 tracks - current track
            ∟ timetoplay - time after which need to make next request to get new current playing
        other tracks - previous played (9 tracks)
        """
        latest_tracks = []
        res = req_post(self.current_playing_url, data={'origin': 'website'})
        res = json_loads(res.text)['tracks']

        for one_track in res:
            seconds_to_play = one_track.get('timetoplay', 0)
            seconds_playing = int(one_track['duration']) - seconds_to_play
            start_date = datetime.now() - timedelta(seconds=seconds_playing)
            end_date = start_date + timedelta(seconds=seconds_to_play)

            spotify = one_track['spotify']
            if spotify:
                spotify = spotify.get('id', '').split('track:')[-1]

            deezer = one_track['deezer']
            if deezer:
                deezer = deezer.get('id', '')

            track_dict = {

                'artist': one_track['artist'],
                'title': one_track['title'],
                'common_name': f"{one_track['artist']} - {one_track['title']}",
                'timetoplay': seconds_to_play,
                'spotify': spotify,
                'deezer': deezer,
                'radio_name': self.radio_id,
                'start_date': start_date,
                'end_date': end_date
            }
            latest_tracks.append(track_dict)

        return latest_tracks

    # todo: unify current tracks output for all radios
    # todo: as Djam gives 9 tracks from now to past, dump it maybe to separate DB which will overrides
    #  dumping tracks to separate DB will prevent many requests from users to grab tracks from radio site
    #  save spotify/dizer links to songs?
    # todo: keep grabbing tracks in real time, with Scheduler? (1 request according to time to play?)
    #             "duration": "181",
    #             "timetoplay": 127,
