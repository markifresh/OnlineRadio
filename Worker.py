import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from secret_data import radio_api_key
from requests import get, post
from json import loads
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from traceback import format_exc as traceback_format_exc
from time import sleep

import logging
# logging.basicConfig(filename='logs.txt', level=logging.INFO)
sqla_logger = logging.getLogger('sqlalchemy.engine.base.Engine')

########### disable log prints to console ############
for hdlr in sqla_logger.handlers:
    sqla_logger.removeHandler(hdlr)
######################################################

sqla_logger.propagate = False
sqla_logger.setLevel(logging.INFO)
sqla_logger.addHandler(logging.FileHandler('sqla.log'))

class DBWorker:

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{config.db_location}', echo=False)
        # datetime.today().date() - timedelta(days=1)
        cur_time = datetime.today()
        from_date = datetime(cur_time.year, cur_time.month, cur_time.day, 0, 0) - timedelta(days=1)
        till_date = from_date + timedelta(hours=23, minutes=59)
        self.play_date = from_date.strftime('%d/%m/%Y')
        self.start_time = str(int(from_date.timestamp()))
        self.end_time = str(int(till_date.timestamp()))
        self.yesterday_tracks = []



    def create_db_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def commit_data(self, data, session=''):
        if not session:
            session = self.create_db_session()
        if isinstance(data, list) or isinstance(data, tuple):
            session.add_all(data)
        else:
            session.add(data)

        try:
            session.commit()
            result = {'success': True, 'result': ''}
        except:
            result = {'success': False, 'result': traceback_format_exc()}

        session.close()
        return result

    def update_row(self, model, filter_id, data):
        session = self.create_db_session()
        object = session.query(model).filter(model.id == filter_id)
        if object.count() == 1:
            try:
                object.update(data)
                session.commit()
                result = {'success': True, 'result': ''}
            except:
                result = {'success': False, 'result': traceback_format_exc()}

        else:
            result = {'success': False, 'result': f'Instead of 1 - {object.count} object was found'}

        session.close()
        return result


    def get_fip_stations(self):
        res_list = []
        json = {'query': '{ brand'
        f'(id: {config.fip_radio["id"]}) '
                         '{ id webRadios { id } } } '}
        headers = {'x-token': radio_api_key}
        res = post(url=config.url_api_open_radio, json=json, headers=headers)

        if res.status_code != 200:
            return {'success': False, 'result': res.status_code, 'respond': res.text}

        radios = loads(res.text)['data']['brand']['webRadios']
        fip_stations = [(radio['id']) for radio in radios]
        fip_stations.append(config.fip_radio['id'])
        for excluded_station in config.exclude_radios:
            if excluded_station in fip_stations:
                fip_stations.remove(excluded_station)

        for fip_station in fip_stations:
            res_list.append({'id': fip_station, 'url': config.fip_radio['url']})

        return {'success': True, 'result': res_list, 'respond': ''}


    def update_radios_list_db(self, RadioModel):
        failed_radios = []
        updated_radios = []
        radios = self.get_fip_stations()

        if not radios['success']:
            return radios

        radios = radios['result']
        radios.append(config.djam_radio)

        db_session = self.create_db_session()
        db_radios = db_session.query(RadioModel).all()
        db_radios = str(db_radios)
        db_session.close()

        for radio in radios:
            if f'<Radio({radio["id"]})>' not in db_radios:
                res = self.commit_data(RadioModel(id=radio['id'], url=radio['url']))
                if res['success']:
                    updated_radios.append(radio["id"])
                else:
                    radio['error'] = res['result']
                    failed_radios.append(radio)

        return {'success': len(failed_radios) == 0, 'updated': updated_radios, 'failed': failed_radios}

    # todo: add method to get all imports for today / or statistics num_requested vs num_added


    def get_fip_radio_tracks(self, radio_id, play_date):
        if isinstance(play_date, str) and '/' in play_date:
            orig_date = play_date
            day, month, year = play_date.split('/')[:3]             #06/09/2020
            day, month, year = int(day), int(month), int(year)
            play_date = datetime(year=year, month=month, day=day)

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

            genre = radio_id.split('_')[-1].lower()
            url = config.fip_radio['tracks_request_url']
            json = {'query': '{ grid'
                             f'(start: {start_time}, end: {end_time}, station: {radio_id}) '
                             '{ ... on TrackStep { start track  { mainArtists title albumTitle } } } }  ' }
            headers = {'x-token': radio_api_key}
            res = post(url=url, json=json, headers=headers)
            if res.status_code != 200:
                return {'success': False, 'result': 'Failed to get tracks from API', 'respond': ''}

            tracks = loads(res.text)['data']['grid']
            for track in tracks:
                play_date = self.play_date
                play_time = track.get('start', '')
                if play_time:
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
                                     'radio_id': radio_id,
                                     'genre': genre})
            sleep(2)

        return {'success': True, 'result': res_list, 'respond': ''}



    def get_yesterday_fip_radio_tracks(self, radio_id):
        return self.get_fip_radio_tracks(radio_id, datetime.now() - timedelta(days=1))


    def get_djam_radio_tracks(self, play_date):
        if isinstance(play_date, str) and '/' in play_date:
            orig_date = play_date
            day, month, year = play_date.split('/')[:3]             #06/09/2020
            day, month, year = int(day), int(month), int(year)
            play_date = datetime(year=year, month=month, day=day)

        elif isinstance(play_date, datetime):
            orig_date = play_date.strftime('%d/%m/%Y')
            day = play_date.day
            play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)

        else:
            return {'success': False, 'result': 'incorrect date format', 'respond': ''}

        res_list = []
        url = config.djam_radio['tracks_request_url']

        # receives tracks 15 mins before and 15 mins after time in request
        # so need to use time step 30 mins for requests, f.e. 9.00 -- 9.30 -- 10.00 ...
        while play_date.day == day:
            data = {'day': str(play_date.day),
                    'month': str(play_date.month),
                    'hour': str(play_date.hour),
                    'minute': '0'}

            res = post(url, json=data)
            if res.status_code != 200:
                return {'success': False, 'result': res.status_code, 'respond': res.text}

            page_parsed = BeautifulSoup(res.text, 'html.parser')
            lis = page_parsed.select('li')
            for li in lis:
                track_str = li.text
                play_time, common_name = track_str.split(' : ')
                play_time = play_time.replace('h', ':')
                title, artist = common_name.split(' - ')
                common_name = f'{artist} - {title}'
                res_list.append({
                                  'artist': artist,
                                  'title': title,
                                  'play_date': f'{orig_date} {play_time}',
                                  'common_name': common_name,
                                  'genre': 'djam'
                                 })

            play_date += timedelta(minutes=30)

        return {'success': len(res_list) > 0, 'result': res_list, 'respond': ''}

    def get_yesterday_djam_radio_tracks(self):
        return self.get_djam_radio_tracks(datetime.now() - timedelta(days=1))



    def get_yesterday_radio_tracks(self, RadioObj):
        radio_id = RadioObj if isinstance(RadioObj, str) else RadioObj.id

        try:
            if radio_id == config.djam_radio['id']:
                return self.get_yesterday_djam_radio_tracks()

            elif config.fip_radio['id'] in radio_id:
                return self.get_yesterday_fip_radio_tracks(radio_id)
        except:
            return {'success': False, 'result': 'Failed to get tracks', 'respond': traceback_format_exc()}

        return {'success': False, 'result': 'Radio ID not in condition list', 'respond': ''}



    # def get_all_tracks(self):
    #     tracks = []
    #     fip = self.get_yesterday_fip_tracks()
    #     djam = self.get_yesterday_djam_radio_tracks()
    #
    #     if fip['success'] and djam['success']:
    #         tracks = fip['result'] + djam['result']
    #
    #     return {'success': len(tracks) > 0, 'result': tracks}



    def update_radio_tracks(self, RadioObj, TrackModel, DBImportModel):
        failed_tracks = []
        updated_tracks = []
        already_added_tracks = []
        radioObject_id = RadioObj.id

        radio_tracks = self.get_yesterday_radio_tracks(RadioObj)

        if not radio_tracks['success']:
            return radio_tracks

        radio_tracks = radio_tracks['result']

        db_session = self.create_db_session()
        db_tracks = [track[0] for track in db_session.query(TrackModel.common_name).all()]
        db_session.close()

        import_time = datetime.now()
        import_id = import_time.strftime('%d/%m/%Y %H:%M:%S.%f')
        self.commit_data(DBImportModel(id=import_id, radio_id=radioObject_id))
        for track in radio_tracks:
            # db_session = self.create_db_session()
            # new_track = db_session.query(TrackModel).filter_by(common_name=track["common_name"]).scalar() is None
            # db_session.close()
            # if new_track:
            if track["common_name"] not in db_tracks:
                res = self.commit_data(TrackModel(
                        common_name=track['common_name'],
                        radio_id=radioObject_id,
                        play_date=track['play_date'],
                        title=track['title'],
                        artist=track['artist'],
                        album_name=track.get('album_name', ''),
                        db_import_id=import_id,
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
        self.update_row(DBImportModel, import_id, {'num_tracks_added': num_tracks_added,
                                                   'num_tracks_requested': num_tracks_requested})

        return {'success': len(failed_tracks) == 0, 'updated': updated_tracks, 'failed': failed_tracks}


    def get_artists(self):
        pass
        # return {artist[0] for artist in ses.query(Track.artist).all()}


    # def get_artists_tracks(self, artist):
    #     tracks = ses.query(Track).filter(Track.artist.like(artist)).all()

    # https://developers.radiofrance.fr/
    # https://www.radiofrance.fr/lopen-api-radio-france
    # "https://docs.google.com/document/d/1SKWunSLpuUtWyaRqrZCI70vNpq_nNCTxeNNVfyCSaPc/edit#"

    # https://api.radiofrance.fr/livemeta/pull/7


    #
    #
    # print(unquote("https://www.fip.fr/latest/api/graphql?operationName=History&variables=%7B%22"
    #               "first%22%3A10%2C%22"
    #               "after%22%3A%22MTU5OTAxNTQzOA%3D%3D%22%2C%22"
    #               "stationId%22%3A7%2C%22"
    #               "preset%22%3A%22192x192%22%7D&"
    #               "extensions=%7B%22"
    #               "persistedQuery%22%3A%7B%22"
    #               "version%22%3A1%2C%22"
    #               "sha256Hash%22%3A%227530970d2ffdf4b2cb739123898944594f32dcfa4060c9b49e9e41d54d9f7857%22%7D%7D"))
    #
    # res = 'https://www.fip.fr/latest/api/graphql?operationName=History&variables={' \
    #       '"first":10,' \
    #       '"after":"MTU5OTAxNTQzOA==",' \
    #       '"stationId":7,' \
    #       '"preset":"192x192"}&' \
    #       'extensions={' \
    #         '"persistedQuery":{' \
    #             '"version":1,' \
    #             '"sha256Hash":"7530970d2ffdf4b2cb739123898944594f32dcfa4060c9b49e9e41d54d9f7857"}}'
    #
    # pass


