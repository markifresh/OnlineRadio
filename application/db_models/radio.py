from application.db_models import tracks_import
from application.db_models import tracks_export
from application.db_models import track
from application.workers.ExtraFunc import get_date_range_list
from application.workers import RadioWorker

from config import RadioConfig, APIConfig
from json import loads
from requests import post as request_post

from application.db_models.extenders_for_db_models import BaseExtended

from sqlalchemy import Column, Integer, String, Sequence, DateTime, JSON
from sqlalchemy.orm import relationship
from traceback import format_exc as traceback_format_exc
from datetime import datetime, timedelta, date

from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# class RadioExternalFunctions:
#
#     @classmethod
#     def get_fip_stations(cls):
#         json = {'query': '{ brand'
#         f'(id: {RadioConfig.fip_radio["id"]}) '
#                          '{ id liveStream webRadios { id liveStream} } } '}
#         headers = {'x-token': APIConfig.radio_api_key}
#         res = request_post(url=RadioConfig.fip_radio['tracks_request_url'], json=json, headers=headers)
#
#         if res.status_code != 200:
#             return {'success': False, 'result': res.status_code, 'respond': res.text}
#         radio_url = RadioConfig.fip_radio['url']
#         radio = loads(res.text)['data']['brand']
#         radios = radio['webRadios']
#         fip_radio = {'name': radio['id'],
#                      'url': radio_url,
#                      'stream_url': radio['liveStream']}
#         fip_stations = {}
#         for radio in radios:
#             fip_stations[radio['id']] = {'name': radio['id'],
#                                          'url': radio_url,
#                                          'stream_url': radio['liveStream']}
#         fip_stations[fip_radio['name']] = fip_radio
#
#         for excluded_station in RadioConfig.exclude_radios:
#             if excluded_station in fip_stations:
#                 del fip_stations[excluded_station]
#
#         return {'success': True, 'result': fip_stations, 'respond': ''}
#
#     @classmethod
#     def get_djam_radio_now_tracks(cls):
#         """
#         0 tracks - current track
#             ∟ timetoplay - time after which need to make next request to get new current playing
#         other tracks - previous played (9 tracks)
#         """
#         res = request_post(RadioConfig.djam_radio['current_playing_url'], data={'origin': 'website'})
#         return loads(res.text)['tracks']
#
#     @classmethod
#     def get_fip_radio_now_track(cls, radio_name):
#         orig_date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
#         url = RadioConfig.fip_radio['tracks_request_url']
#         json = {'query': '{ live'
#                          f'(station: {radio_name}) '
#                          '{ song { start end track  { mainArtists title  } } } }  '}
#
#         headers = {'x-token': APIConfig.radiofrance_api_key}
#         res = request_post(url=url, json=json, headers=headers)
#
#         if res.status_code != 200:
#             return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}
#         track = loads(res.text)['data']['live']['song']
#
#         play_time = track.get('start', '')
#         if not play_time:
#             start_date = orig_date
#         else:
#             start_date = datetime.fromtimestamp(play_time).strftime('%d/%m/%Y %H:%M:%S')
#
#         end_time = track.get('end', '')
#         if not end_time:
#             end_date = orig_date
#         else:
#             end_date = datetime.fromtimestamp(end_time).strftime('%d/%m/%Y %H:%M:%S')
#
#         track = track['track']
#         if track:
#             artist = ','.join(track.get('mainArtists', '')).strip()
#             title = track.get('title', '').strip()
#             common_name = f'{artist} - {title}'
#             return {'album_name': track.get('albumTitle', ''),
#                              'common_name': common_name,
#                              'artist': artist,
#                              'title': title,
#                              'start_date': start_date,
#                              'end_date': end_date,
#                              'radio_name': radio_name}
#
#         return {}
#
#     @classmethod
#     def get_fip_radio_now_tracks(cls, radio_name):
#         end_time = datetime.now()
#         orig_date = end_time.strftime('%d-%m-%Y')
#         start_time = end_time - timedelta(minutes=15)
#         start_time = str(int(start_time.timestamp()))
#         end_time = str(int(end_time.timestamp()))
#
#         res_list = []
#         genre = radio_name.split('_')[-1].lower()
#         url = RadioConfig.fip_radio['tracks_request_url']
#         json = {'query': '{ grid'
#                          f'(start: {start_time}, end: {end_time}, station: {radio_name}) '
#                          '{ ... on TrackStep { start track  { mainArtists title albumTitle } } } }  '}
#
#         headers = {'x-token': APIConfig.radio_api_key}
#         res = request_post(url=url, json=json, headers=headers)
#
#         if res.status_code != 200:
#             return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}
#         tracks = loads(res.text)['data']['grid']
#
#         for track in tracks:
#             play_time = track.get('start', '')
#             if not play_time:
#                 play_date = orig_date
#             else:
#                 play_date = datetime.fromtimestamp(play_time).strftime('%d/%m/%Y %H:%M:%S')
#             track = track['track']
#             if track:
#                 artist = ','.join(track.get('mainArtists', '')).strip()
#                 title = track.get('title', '').strip()
#                 common_name = f'{artist} - {title}'
#                 res_list.append({'album_name': track.get('albumTitle', ''),
#                                  'common_name': common_name,
#                                  'artist': artist,
#                                  'title': title,
#                                  'play_date': play_date,
#                                  'radio_name': radio_name,
#                                  'genre': genre})
#
#         return {'success': True, 'result': res_list, 'respond': ''}
#
#     @classmethod
#     def get_djam_radio_tracks(cls, play_date):
#         request_time = datetime.now()
#         if isinstance(play_date, str) and '-' in play_date:
#             day, month, year = play_date.split('-')[:3]             #06/09/2020
#             day, month, year = int(day), int(month), int(year)
#             play_date = datetime(year=year, month=month, day=day)
#
#         elif isinstance(play_date, (datetime, date)):
#             day = play_date.day
#             play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)
#
#         else:
#             return {'success': False, 'result': 'incorrect date format', 'respond': ''}
#
#         url = RadioConfig.djam_radio['tracks_request_url']
#         responds_list = []
#         res_list = []
#         dates_list = []
#         dates_list.append(play_date)
#         time_step_min = 30
#         play_date += timedelta(minutes=time_step_min)
#
#         while play_date.day == day:
#             dates_list.append(play_date)
#             play_date += timedelta(minutes=time_step_min)
#
#         def get_jam_tracks_threads(one_date):
#             data = {'day': one_date.day, 'month': one_date.month, 'hour': one_date.hour, 'minute': one_date.minute}
#             res = request_post(url, data=data)
#             responds_list.append((res.status_code, res.text))
#             elements = BeautifulSoup(res.text, 'html.parser').find_all('li')
#             for li in elements:
#                 track_str = li.text
#                 if 'Cinema' not in track_str and 'Ledjam Radio' not in track_str:
#                     splited = track_str.split(' : ')
#                     hours, minutes = splited[0].split('h')
#                     track_play_date = datetime(day=one_date.day,
#                                                month=one_date.month,
#                                                year=one_date.year,
#                                                hour=int(hours),
#                                                minute=int(minutes))
#                     common_name = ':'.join(splited[1:]).split('-')
#                     title = common_name[0].strip()
#                     artist = ('-'.join(common_name[1:])).strip()
#                     common_name = f'{artist} - {title}'
#                     res_list.append({
#                         'artist': artist,
#                         'title': title,
#                         'play_date': track_play_date,
#                         'common_name': common_name,
#                         'genre': 'djam'
#                     })
#
#         with ThreadPoolExecutor(max_workers=20) as executor:
#             executor.map(get_jam_tracks_threads, dates_list)
#
#         return {'success': True, 'result': res_list, 'responds_list': responds_list, 'respond': '',
#                 'for_day': play_date, 'request_time': request_time}
#
#     @classmethod
#     def get_djam_radio_tracks_selenium(cls, play_date):
#         if isinstance(play_date, str) and '-' in play_date:
#             orig_date = play_date
#             day, month, year = play_date.split('-')[:3]             #06/09/2020
#             day, month, year = int(day), int(month), int(year)
#             play_date = datetime(year=year, month=month, day=day)
#
#         elif isinstance(play_date, (datetime, date)):
#             orig_date = play_date.strftime('%d/%m/%Y')
#             day = play_date.day
#             play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)
#
#         else:
#             return {'success': False, 'result': 'incorrect date format', 'respond': ''}
#
#         options = webdriver.ChromeOptions()
#         options.add_argument('headless')
#         options.add_argument('kiosk')
#         browser = webdriver.Chrome(options=options)
#
#         res_list = []
#         try:
#
#             browser.get('https://www.djamradio.com')
#             sleep(2)
#             browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             sleep(2)
#             find_button = browser.find_element_by_partial_link_text('Find a song')
#             find_button.click()
#             sleep(2)
#
#             day_str = play_date.strftime('%d').lstrip('0')
#             month = (play_date - timedelta(30)).month
#
#             day_drop = Select(browser.find_element_by_id('retrieve_day'))
#             month_drop = Select(browser.find_element_by_id('retrieve_month'))
#             hour_drop = Select(browser.find_element_by_id('retrieve_hour'))
#             minute_drop = Select(browser.find_element_by_id('retrieve_min'))
#
#             day_drop.select_by_value(day_str)
#             month_drop.select_by_index(month)
#
#             while play_date.day == day:
#                 #print(play_date)
#                 hour = play_date.strftime('%H')
#                 if hour[0] == '0':
#                     hour = hour[1]
#
#                 minute = play_date.strftime('%M')
#                 if minute[0] == '0':
#                     minute = minute[1]
#
#                 hour_drop.select_by_value(hour)
#                 minute_drop.select_by_value(minute)
#                 btn = browser.find_element_by_css_selector('#form_retrieve .btn')
#                 btn.click()
#                 sleep(2)
#
#                 elements = browser.find_elements_by_css_selector('#retrieve_results li')
#                 for li in elements:
#                     track_str = li.text
#                     splited = track_str.split(' : ')
#                     play_time = splited[0].replace('h', ':')
#                     common_name = ':'.join(splited[1:]).split('-')
#                     title = common_name[0].strip()
#                     artist = ('-'.join(common_name[1:])).strip()
#                     common_name = f'{artist} - {title}'
#                     res_list.append({
#                         'artist': artist,
#                         'title': title,
#                         'play_date': f'{orig_date} {play_time}',
#                         'common_name': common_name,
#                         'genre': 'djam'
#                     })
#
#                 play_date += timedelta(minutes=30)
#
#             browser.close()
#             return {'success': True, 'result': res_list, 'respond': ''}
#
#         except:
#             browser.close()
#             return {'success': False, 'result': traceback_format_exc(), 'respond': ''}
#
#
#     @classmethod
#     def get_fip_radio_tracks(cls, radio_name, play_date):
#         request_time = datetime.now()
#
#         if isinstance(play_date, str) and '-' in play_date:
#             orig_date = play_date
#             day, month, year = play_date.split('-')[:3]             #06/09/2020
#             day, month, year = int(day), int(month), int(year)
#             play_date = datetime(year=year, month=month, day=day)
#             orig_date = orig_date.replace('-', '/')
#
#         elif isinstance(play_date, (datetime, date)):
#             orig_date = play_date.strftime('%d/%m/%Y')
#             day = play_date.day
#             play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)
#
#         else:
#             return {'success': False, 'result': 'incorrect date format', 'respond': ''}
#
#         from_date = play_date
#         responds_list = []
#         res_list = []
#         dates_list = []
#         dates_list.append(from_date)
#         time_step = 4
#         from_date += timedelta(hours=time_step)
#
#         while from_date.day == day:
#             dates_list.append(from_date)
#             from_date += timedelta(hours=time_step)
#
#         def get_tracks_by_threads(one_date):
#             start_time = str(int(one_date.timestamp()))
#             end_time = str(int((one_date + timedelta(hours=time_step)).timestamp()))
#
#             genre = radio_name.split('_')[-1].lower()
#             url = RadioConfig.fip_radio['tracks_request_url']
#             json = {'query': '{ grid'
#                              f'(start: {start_time}, end: {end_time}, station: {radio_name}) '
#                              '{ ... on TrackStep { start track  { mainArtists title albumTitle } } } }  ' }
#             headers = {'x-token': APIConfig.radio_api_key}
#             res = request_post(url=url, json=json, headers=headers)
#             responds_list.append((res.status_code, res.text))
#             if res.status_code != 200:
#                 return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}
#
#             tracks = loads(res.text)['data']['grid']
#             for track in tracks:
#                 play_time = track.get('start', '')
#                 track_play_date = datetime.fromtimestamp(play_time)
#
#                 track = track['track']
#                 if track:
#                     artist = ','.join(track.get('mainArtists', '')).strip()
#                     title = track.get('title', '').strip()
#                     common_name = f'{artist} - {title}'
#                     res_list.append({'album_name': track.get('albumTitle', ''),
#                                      'common_name': common_name,
#                                      'artist': artist,
#                                      'title': title,
#                                      'play_date': track_play_date,
#                                      'radio_name': radio_name,
#                                      'genre': genre})
#
#         with ThreadPoolExecutor(max_workers=15) as executor:
#             executor.map(get_tracks_by_threads, dates_list)
#
#         return {'success': True, 'result': res_list, 'responds_list': responds_list, 'respond': '',
#                 'for_date': play_date, 'request_time': request_time}
#
#     @classmethod
#     def get_radio_tracks(cls, radio_name, play_date):
#         try:
#             if radio_name == RadioConfig.djam_radio['id']:
#                 return cls.get_djam_radio_tracks(play_date)
#
#             elif RadioConfig.fip_radio['id'] in radio_name:
#                 return cls.get_fip_radio_tracks(radio_name, play_date)
#         except:
#             return {'success': False, 'result': 'Failed to get tracks', 'respond': traceback_format_exc()}
#
#         return {'success': False, 'result': 'Radio ID not in condition list', 'respond': ''}
#
#
#
#     @classmethod
#     def get_radio_tracks_per_range(cls, radio_name, start_date=None, end_date=None):
#         res = []
#         futures = []
#         calendar = get_date_range_list(start_date, end_date)
#
#         with ThreadPoolExecutor(max_workers=16) as executor:
#             for one_day in calendar:
#                 futures.append(executor.submit(cls.get_radio_tracks, radio_name, one_day))
#         for future in as_completed(futures):
#             res.append(future.result())
#
#         return res

class  Radio(BaseExtended):
    unique_search_field = 'name'

    __tablename__ = 'radios'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), Sequence('radio_name_seq'), unique=True)  # id from api
    url = Column(String(80))
    stream_url = Column(String(80))
    db_imports = relationship('tracks_import.TracksImport', lazy='dynamic')
    spotify_exports = relationship('tracks_export.TracksExport', lazy='dynamic')
    tracks = relationship('track.Track', lazy='dynamic')
    created_on = Column(DateTime(), default=datetime.now)
    currently_playing = Column(JSON)    # make hybrid, based on scheduled background function/variable ?
    description = Column(String)
    genre = Column(String)
    country = Column(String)

    def __repr__(self):
        return f"<Radio({self.name})>"



    @classmethod
    def update_radios_list(cls):
        failed_radios = []
        updated_radios = []
        radios = RadioWorker.get_all_radios()

        if not radios['success']:
            return radios

        radios = radios['result']

        db_radios = [radio[0] for radio in cls.session.query(cls.name).all()]
        # cls.session.close()

        for radio in radios:
            if radio not in db_radios:
                res = cls.commit_data(radios[radio])

                if res['success']:
                    updated_radios.append(radio)

                else:
                    radios[radio]['error'] = res['result']
                    failed_radios.append(radios[radio])

        return {'success': len(failed_radios) == 0, 'updated': updated_radios, 'failed': failed_radios}

    @classmethod
    def update_all_radios_tracks(cls):
        results = {}
        radios = cls.all()
        for radio in radios:

            try:
                res = cls.update_radio_tracks(radio_name=radio.name)
                results[radio.name] = res

            except:
                results['dd'] = {'success': False, 'result': traceback_format_exc()}

        return results

    @classmethod
    def import_tracks_to_db(cls, radio_name, day, start_time, radio_tracks):
        updated_tracks = []
        failed_tracks = []
        already_added_tracks = []
        db_tracks = [track[0] for track in cls.session.query(track.Track.common_name).all()]
        import_date = datetime.now()
        # import_date = import_time.strftime('%d/%m/%Y %H:%M:%S.%f')
        if day:
            cls.commit_data(tracks_import.TracksImport(import_date=import_date, radio_name=radio_name, for_date=day))
        else:
            cls.commit_data(tracks_import.TracksImport(import_date=import_date, radio_name=radio_name))
        for track in radio_tracks:
            # db_session = self.create_db_session()
            # new_track = db_session.query(TrackModel).filter_by(common_name=track["common_name"]).scalar() is None
            # db_session.close()
            # if new_track:
            if track["common_name"] not in db_tracks:
                res = cls.commit_data(track.Track(
                    common_name=track['common_name'],
                    radio_name=radio_name,
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

        end = datetime.now()
        import_duration = round((end - start_time).total_seconds(), 2)
        num_tracks_added = len(updated_tracks)
        num_tracks_requested = len(radio_tracks)
        res = tracks_import.TracksImport.update_row(data={'import_date': import_date,
                                                    'num_tracks_added': num_tracks_added,
                                                    'num_tracks_requested': num_tracks_requested,
                                                    'import_duration': import_duration})

        return {'success': res['success'],
                'updated': updated_tracks,
                'already_added': already_added_tracks,
                'failed': failed_tracks,
                'total tracks number': num_tracks_requested,
                'num_tracks_requested': num_tracks_requested,
                'num_tracks_added': num_tracks_added,
                'tracks': radio_tracks,
                'update_time_sec': import_duration,
                'import_date': import_date.strftime('%d-%m-%Y %H:%M:%S'),
                'for_date': str(day),
                'res': res}

    @classmethod
    def update_radio_tracks(cls, radio_name, day=datetime.now()-timedelta(days=1)):
        start = datetime.now()
        radio_tracks = RadioWorker.create_radio(radio_name).get_radio_tracks(day)

        if not radio_tracks['success']:
            return radio_tracks

        return cls.import_tracks_to_db(radio_name, day, start, radio_tracks['result'])



    @classmethod
    def update_radio_tracks_per_range(cls, radio_name, start_date=None, end_date=None):
        start_time = datetime.now()
        tracks = []
        tracks_req = RadioWorker.create_radio(radio_name).get_radio_tracks_per_range(start_date, end_date)

        for result in tracks_req:
            if result['success']:
                tracks += result['result']
            else:
                return {'success': False, 'result': tracks_req}

        return cls.import_tracks_to_db(radio_name=radio_name, day=None, start_time=start_time, radio_tracks=tracks)


    @classmethod
    def get_radio_by_name(cls, name):
        radio = cls.query(cls).filter(cls.name == name).one_or_none()
        if not radio:
            return {}

        radio_dic = cls.to_json(radio)
        radio_dic[name]['num_tracks'] = track.Track.get_tracks_per_radio_num(name)
        radio_dic[name]['latest_dbimport'] = getattr(tracks_import.TracksImport.get_latest_import_for_radio(name), 'import_date', '-')
        return radio_dic[name]

    @classmethod
    def get_radios_by_name(cls, names):
        final_res = []
        radios = cls.query(cls).filter(cls.name.in_(names)).all()

        for radio in radios:
            radio_dic = cls.to_json(radio)
            radio_dic[radio.name]['num_tracks'] = track.Track.get_tracks_per_radio_num(radio.name)
            radio_dic[radio.name]['latest_dbimport'] = getattr(tracks_import.TracksImport.get_latest_import_for_radio(radio.name), 'import_date', '-')
            final_res.append(radio_dic[radio.name])

        return final_res

    @classmethod
    def get_all_radios(cls):
        return cls.to_json(cls.all())

    @classmethod
    def get_data_for_radios_page(cls):
        radios = cls.all()
        for radio in radios:
            radio.num_tracks = track.Track.get_tracks_per_radio_num(radio.name)
            db_import = tracks_import.TracksImport.get_latest_import_for_radio(radio.name)
            radio.latest_dbimport = db_import.import_date.strftime('%d-%m-%Y %H:%M:%S') if db_import else None
            spotify_export = tracks_export.TracksExport.get_latest_export_for_radio(radio.name)
            radio.latest_spotify_export = \
                spotify_export.export_date.strftime('%d-%m-%Y %H:%M:%S') if spotify_export else None
            radio.to_export_num_tracks = track.Track.get_tracks_exported_not_per_radio_num(radio_name=radio.name)
        return radios


    @classmethod
    def export_tracks(cls, radio_name, limit=100):
        num_tracks_added = 0
        export_date = datetime.now()
        tracks = track.Track.get_tracks_exported_not_per_radio(radio_name, end_id=limit)
        # tracks = [f'{track["artist"]} - {track["title"]}' for track in tracks]
        cls.commit_data(tracks_export.TracksExport(export_date=export_date,
                                                   radio_name=radio_name,
                                                   num_tracks_requested=len(tracks)))

        from application.apis.spotify_api import create_obj
        sp = create_obj()
        playlist = sp.get_user_playlist_by_name(radio_name)

        if not playlist['success']:
            playlist = sp.create_user_playlist(name=radio_name)

        ress = sp.add_tracks_to_playlist(radio_name, tracks)
        if not ress['success']:
            ress['export_date'] = export_date.strftime('%d-%m-%Y %H:%M:%S')
            print(ress)
            return ress

        num_tracks_requested = len(ress['failed_to_find']) + len(ress['errored'])
        for res in ress['result']:
            print(res)
            num_tracks_requested += len(res.get('added', ''))
            if res['success']:
                num_tracks_added += len(res.get('added', ''))
                for track in res['added']:
                    track['spotify_export_date'] = export_date
                    track.Track.update_row(data=track)

        for track in ress['failed_to_find']:
            track.Track.update_row(data={'common_name': track,
                                            'failed_to_spotify': 'True',
                                            'spotify_export_date': export_date})

        tracks_export.TracksExport.update_row(data={'export_date': export_date,
                                                        'num_tracks_added': num_tracks_added,
                                                        'num_tracks_requested': num_tracks_requested})

        ress['export_date'] = export_date.strftime('%d-%m-%Y %H:%m:%S')
        ress['num_tracks_added'] = num_tracks_added
        ress['num_tracks_exported'] = num_tracks_added + len(ress['failed_to_find'])
        ress['num_tracks_requested'] = num_tracks_requested
        return ress
