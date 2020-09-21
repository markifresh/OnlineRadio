from config import RadioConfig, APIConfig
from json import loads
from requests import post as request_post

from application.db_models.extenders_for_db_models import BaseExtended

from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship
from traceback import format_exc as traceback_format_exc
from datetime import datetime, timedelta

from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select

class RadioExternalFunctions:

    @classmethod
    def get_fip_stations(cls):
        res_list = []
        json = {'query': '{ brand'
        f'(id: {RadioConfig.fip_radio["id"]}) '
                         '{ id webRadios { id } } } '}
        headers = {'x-token': APIConfig.radio_api_key}
        res = request_post(url=RadioConfig.fip_radio['tracks_request_url'], json=json, headers=headers)

        if res.status_code != 200:
            return {'success': False, 'result': res.status_code, 'respond': res.text}

        radios = loads(res.text)['data']['brand']['webRadios']
        fip_stations = [(radio['id']) for radio in radios]
        fip_stations.append(RadioConfig.fip_radio['id'])
        for excluded_station in RadioConfig.exclude_radios:
            if excluded_station in fip_stations:
                fip_stations.remove(excluded_station)

        for fip_station in fip_stations:
            res_list.append({'id': fip_station, 'url': RadioConfig.fip_radio['url']})

        return {'success': True, 'result': res_list, 'respond': ''}

    @classmethod
    def get_djam_radio_tracks_selenium(cls, play_date):
        if isinstance(play_date, str) and '-' in play_date:
            orig_date = play_date
            day, month, year = play_date.split('-')[:3]             #06/09/2020
            day, month, year = int(day), int(month), int(year)
            play_date = datetime(year=year, month=month, day=day)

        elif isinstance(play_date, datetime):
            orig_date = play_date.strftime('%d/%m/%Y')
            day = play_date.day
            play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)

        else:
            return {'success': False, 'result': 'incorrect date format', 'respond': ''}

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('kiosk')
        browser = webdriver.Chrome(options=options)

        res_list = []
        try:

            browser.get('https://www.djamradio.com')
            sleep(2)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
            find_button = browser.find_element_by_partial_link_text('Find a song')
            find_button.click()
            sleep(2)

            day_str = play_date.strftime('%d').lstrip('0')
            month = (play_date - timedelta(30)).month

            day_drop = Select(browser.find_element_by_id('retrieve_day'))
            month_drop = Select(browser.find_element_by_id('retrieve_month'))
            hour_drop = Select(browser.find_element_by_id('retrieve_hour'))
            minute_drop = Select(browser.find_element_by_id('retrieve_min'))

            day_drop.select_by_value(day_str)
            month_drop.select_by_index(month)

            while play_date.day == day:
                #print(play_date)
                hour = play_date.strftime('%H')
                if hour[0] == '0':
                    hour = hour[1]

                minute = play_date.strftime('%M')
                if minute[0] == '0':
                    minute = minute[1]

                hour_drop.select_by_value(hour)
                minute_drop.select_by_value(minute)
                btn = browser.find_element_by_css_selector('#form_retrieve .btn')
                btn.click()
                sleep(2)

                elements = browser.find_elements_by_css_selector('#retrieve_results li')
                for li in elements:
                    track_str = li.text
                    splited = track_str.split(' : ')
                    play_time = splited[0].replace('h', ':')
                    common_name = ':'.join(splited[1:]).split('-')
                    title = common_name[0].strip()
                    artist = '-'.join(common_name[1:])
                    common_name = f'{artist} - {title}'
                    res_list.append({
                        'artist': artist,
                        'title': title,
                        'play_date': f'{orig_date} {play_time}',
                        'common_name': common_name,
                        'genre': 'djam'
                    })

                play_date += timedelta(minutes=30)

            browser.close()
            return {'success': True, 'result': res_list, 'respond': ''}

        except:
            browser.close()
            return {'success': False, 'result': traceback_format_exc(), 'respond': ''}

    @classmethod
    def get_yesterday_djam_radio_tracks(cls):
        return cls.get_djam_radio_tracks_selenium(datetime.now() - timedelta(days=1))

    @classmethod
    def get_fip_radio_tracks(cls, radio_name, play_date):
        if isinstance(play_date, str) and '-' in play_date:
            orig_date = play_date
            day, month, year = play_date.split('-')[:3]             #06/09/2020
            day, month, year = int(day), int(month), int(year)
            play_date = datetime(year=year, month=month, day=day)
            orig_date = orig_date.replace('-', '/')

        elif isinstance(play_date, datetime):
            orig_date = play_date.strftime('%d/%m/%Y')
            day = play_date.day
            play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)

        else:
            return {'success': False, 'result': 'incorrect date format', 'respond': ''}

        from_date = play_date
        res_list = []

        while from_date.day == day:
            start_time = str(int(from_date.timestamp()))
            from_date += timedelta(hours=4)
            end_time = str(int(from_date.timestamp()))

            genre = radio_name.split('_')[-1].lower()
            url = RadioConfig.fip_radio['tracks_request_url']
            json = {'query': '{ grid'
                             f'(start: {start_time}, end: {end_time}, station: {radio_name}) '
                             '{ ... on TrackStep { start track  { mainArtists title albumTitle } } } }  ' }
            headers = {'x-token': APIConfig.radio_api_key}
            res = request_post(url=url, json=json, headers=headers)
            if res.status_code != 200:
                return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}

            tracks = loads(res.text)['data']['grid']
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
                                     'radio_name': radio_name,
                                     'genre': genre})
            sleep(2)

        return {'success': True, 'result': res_list, 'respond': ''}

    @classmethod
    def get_yesterday_fip_radio_tracks(cls, radio_name):
        return cls.get_fip_radio_tracks(radio_name, datetime.now() - timedelta(days=1))

    @classmethod
    def get_radio_tracks(cls, radio_name, play_date):
        try:
            if radio_name == RadioConfig.djam_radio['id']:
                return cls.get_djam_radio_tracks_selenium(play_date)

            elif RadioConfig.fip_radio['id'] in radio_name:
                return cls.get_fip_radio_tracks(radio_name, play_date)
        except:
            return {'success': False, 'result': 'Failed to get tracks', 'respond': traceback_format_exc()}

        return {'success': False, 'result': 'Radio ID not in condition list', 'respond': ''}

    @classmethod
    def get_yesterday_radio_tracks(cls, radio_name):
        return cls.get_radio_tracks(radio_name, datetime.now() - timedelta(days=1))




class Radio(BaseExtended, RadioExternalFunctions):
    unique_search_field = 'name'

    __tablename__ = 'radios'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), Sequence('radio_name_seq'), unique=True)  # id from api
    url = Column(String(80))
    db_imports = relationship('DBImport', lazy=True)
    spotify_exports = relationship('SpotifyExport', lazy=True)
    tracks = relationship('Track', lazy=True)

    def __repr__(self):
        return f"<Radio({self.name})>"



    @classmethod
    def update_radios_list(cls):
        failed_radios = []
        updated_radios = []
        radios = cls.get_fip_stations()

        if not radios['success']:
            return radios

        radios = radios['result']
        radios.append(RadioConfig.djam_radio)

        db_radios = [radio[0] for radio in cls.session.query(cls.name).all()]
        cls.session.close()

        for radio in radios:
            if radio["id"] not in db_radios:
                res = cls.commit_data(cls(name=radio['id'], url=radio['url']))
                if res['success']:
                    updated_radios.append(radio["id"])
                else:
                    radio['error'] = res['result']
                    failed_radios.append(radio)

        return {'success': len(failed_radios) == 0, 'updated': updated_radios, 'failed': failed_radios}

    @classmethod
    def update_all_radios_tracks(cls):
        results = {}
        radios = cls.all()
        for radio in radios:

            try:
                res = radio.update_radio_tracks()
                results[radio.name] = res

            except:
                results[radio.name] = {'success': False, 'result': traceback_format_exc()}

        return results

    def update_radio_tracks(self):
        from application.db_models import DBImport, Track
        failed_tracks = []
        updated_tracks = []
        already_added_tracks = []
        radioObject_name = self.name

        radio_tracks = self.get_yesterday_radio_tracks(self.name)

        if not radio_tracks['success']:
            return radio_tracks

        radio_tracks = radio_tracks['result']
        total_tracks_num = len(radio_tracks)

        db_tracks = [track[0] for track in self.session.query(Track.common_name).all()]
        self.session.close()

        import_time = datetime.now()
        import_date = import_time.strftime('%d/%m/%Y %H:%M:%S.%f')
        self.commit_data(DBImport(import_date=import_date, radio_name=radioObject_name))
        db_import = self.session.query(DBImport).filter(DBImport.import_date == import_date).first()
        self.session.close()
        for track in radio_tracks:
            # db_session = self.create_db_session()
            # new_track = db_session.query(TrackModel).filter_by(common_name=track["common_name"]).scalar() is None
            # db_session.close()
            # if new_track:
            if track["common_name"] not in db_tracks:
                res = self.commit_data(Track(
                    common_name=track['common_name'],
                    radio_name=radioObject_name,
                    play_date=track['play_date'],
                    title=track['title'],
                    artist=track['artist'],
                    album_name=track.get('album_name', ''),
                    db_import_date=import_date,
                    genre=track['genre']
                ))
                if res['success']:
                    updated_tracks.append(track["common_name"])
                else:
                    track['error'] = res['result']
                    failed_tracks.append(track)
            else:
                already_added_tracks.append(track)

        num_tracks_added = len(updated_tracks)
        num_tracks_requested = num_tracks_added + len(already_added_tracks)
        res = db_import.update_row(data={'num_tracks_added': num_tracks_added,
                                         'num_tracks_requested': num_tracks_requested})
        print(res)
        return {'success': True,
                'updated': updated_tracks,
                'failed': failed_tracks,
                'total tracks number': total_tracks_num,
                'num_tracks_requested': num_tracks_requested,
                'num_tracks_added': num_tracks_added,
                'tracks': radio_tracks}


    def get_latest_import(self):
        from application.db_models import DBImport
        db_import = self.session.query(DBImport).filter(DBImport.radio_name == self.name).\
                    order_by(DBImport.import_date.desc()).first()
        self.session.close()
        return db_import.import_date.split('.')[0] if db_import else 'no imports'


    @classmethod
    def export_all_radios_data_to_json(cls):
        radios = cls.all()
        js_objects = cls.to_json(radios)
        num_tracks = cls.get_tracks_num_per_radios()
        for radio in radios:
            js_objects[radio.name]['num_tracks'] = num_tracks[radio.name]
            js_objects[radio.name]['latest_dbimport'] = radio.get_tracks_num_per_radio()
        return js_objects

    def get_tracks_num_per_radio(self):
        from application.db_models import Track
        return Track.get_num_tracks_per_radio(self.name)

    @classmethod
    def get_tracks_num_per_radios(cls):
        from application.db_models import Track
        return Track.get_num_tracks_per_radios()

    def get_tracks(self):
        from application.db_models import Track
        return Track.get_tracks_per_radio(self.name)


    # format start_date='18-09-2020', end_date='19-09-2020'
    @classmethod
    def get_tracks_num_per_radios_per_date(cls, radio='', start_date='', end_date=''):
        from application.db_models import Track
        return Track.get_num_tracks_per_radio_per_date(radio, start_date, end_date)

    def get_tracks_num_per_radio_per_date(self, start_date='', end_date=''):
        from application.db_models import Track
        return Track.get_num_tracks_per_radio_per_date(self.name, start_date, end_date)