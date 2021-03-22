from application.radios.RadioAbstract import RadioAbstract
from requests import post as req_post
from json import loads as json_loads
from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from application.workers.ExtraFunc import get_date_range_list, sort_tracks_list


class Djam(RadioAbstract):
    radio_id = 'DJAM'
    url = 'https://www.djamradio.com'
    tracks_request_url = 'https://www.djamradio.com/actions/retrieve.php'
    stream_url = 'https://ledjamradio.ice.infomaniak.ch/ledjamradio.mp3'
    current_playing_url = 'https://www.djamradio.com/actions/infos.php'

    def __init__(self, radio_id=radio_id):
        super().__init__(radio_id)

    def get_radio_tracks(self, play_date):
        request_time = datetime.now()
        if isinstance(play_date, str) and '-' in play_date:
            day, month, year = play_date.split('-')[:3]             #06/09/2020
            day, month, year = int(day), int(month), int(year)
            play_date = datetime(year=year, month=month, day=day)

        elif isinstance(play_date, (datetime, date)):
            day = play_date.day
            play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)

        else:
            return {'success': False, 'result': 'incorrect date format', 'respond': ''}

        responds_list = []
        res_list = []
        dates_list = []
        dates_list.append(play_date)
        time_step_min = 30
        play_date += timedelta(minutes=time_step_min)

        while play_date.day == day:
            dates_list.append(play_date)
            play_date += timedelta(minutes=time_step_min)

        def get_jam_tracks_threads(one_date):
            data = {'day': one_date.day, 'month': one_date.month, 'hour': one_date.hour, 'minute': one_date.minute}
            res = req_post(self.tracks_request_url, data=data)
            responds_list.append((res.status_code, res.text))
            elements = BeautifulSoup(res.text, 'html.parser').find_all('li')
            for li in elements:
                track_str = li.text
                if 'Cinema' not in track_str and 'Ledjam Radio' not in track_str:
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
                    res_list.append({
                        'artist': artist,
                        'title': title,
                        'play_date': track_play_date,
                        'common_name': common_name,
                        'genre': 'djam'
                    })

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(get_jam_tracks_threads, dates_list)

        return {'success': True, 'result': sort_tracks_list(res_list), 'responds_list': responds_list, 'respond': '',
                'for_day': play_date, 'request_time': request_time}


    def get_current_track(self):
        return self.get_latest_tracks()[0]

    def get_latest_tracks(self):
        """
        0 tracks - current track
            ∟ timetoplay - time after which need to make next request to get new current playing
        other tracks - previous played (9 tracks)
        """
        res = req_post(self.current_playing_url, data={'origin': 'website'})
        return json_loads(res.text)['tracks']

    # todo: unify current tracks output for all radios
    # todo: as Djam gives 9 tracks from now to past, dump it maybe to separate DB which will overrides
    #  dumping tracks to separate DB will prevent many requests from users to grab tracks from radio site
    #  save spotify/dizer links to songs?
    # todo: keep grabbing tracks in real time, with Scheduler? (1 request according to time to play?)
    #             "duration": "181",
    #             "timetoplay": 127,
