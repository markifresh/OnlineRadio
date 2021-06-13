from application.db_models.extenders_for_db_models import BaseExtended
from application.db_models import track
from application.db_models import user
from application.db_models import tracks_import

from application.workers import ServiceWorker

from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from flask import session
from datetime import datetime
import config


class TracksExport(BaseExtended):
    unique_search_field = 'export_date'

    __tablename__ = 'tracksExports'
    id = Column(Integer, primary_key=True)
    export_date = Column(DateTime, Sequence('tracksExport_export_date_seq'), unique=True)  # update_time in ms
    requester = Column(String(20), ForeignKey('users.account_id'), nullable=False)
    added_tracks = Column(String)
    not_found_tracks = Column(String)
    failed_to_add_tracks = Column(String)
    import_id = Column(Integer)
    radio_name = Column(String(20), ForeignKey('radios.name'), nullable=False)
    num_tracks_added = Column(Integer, default=0)
    num_tracks_requested = Column(Integer, default=0)
    # num_tracks_reviewed = Column(Integer, default=0)
    service_name = Column(String)
    playlist_id = Column(String)
    # tracks_reviewed = tracs_ref

    def __repr__(self):
        return f"<Export({self.export_date}, {self.radio_name}, " \
               f"{self.num_tracks_requested} vs {self.num_tracks_added})>"


    # todo: method/hybryd for parsing tracks (method to get tracks per export)
    # todo: method to find all tracks from string


    @classmethod
    def query_exports(cls, start_date='', end_date='', start='', end='', q_filter=''):
        q_selector = cls.query(cls.export_date, cls.radio_name, cls.num_tracks_added).order_by(cls.export_date.desc())
        res = cls.query_objects(q_selector=q_selector,
                                q_filter=q_filter,
                                start_date=start_date,
                                end_date=end_date,
                                between_argument='export_date')
        res = cls.limit_objects(res, start, end).all()

        return [{'export_date': export[0].strftime('%Y-%m-%d %H:%M:%S'),
                 'radio_name': export[1],
                 'num_tracks_exported': export[2] if export[2] else 0} for export in res]

    @classmethod
    def get_exports(cls, start_id='', end_id=''):
        return cls.query_exports(start=start_id, end=end_id)

    @classmethod
    def get_exports_per_date(cls, start_date, end_date, start_id='', end_id=''):
        return cls.query_exports(start_date=start_date, end_date=end_date, start=start_id, end=end_id)

    @classmethod
    def get_exports_per_date_num(cls, start_date, end_date):
        return cls.query_objects_num(start_date, end_date, between_argument='export_date')


    @classmethod
    def get_exports_num(cls):
        return cls.query_objects_num()

    @classmethod
    def get_export_by_date(cls, export_date):
        if isinstance(export_date, str):
            export_date = datetime.strptime(export_date, '%Y-%m-%dT%H:%M:%S.%f')
        return cls.query(cls).filter(cls.export_date == export_date).one_or_none()

    @classmethod
    def get_export_tracks(cls, export_date):
        one_export = cls.get_export_by_date(export_date)
        track_db = track.Track
        one_export_tracks = one_export.added_tracks.split(',')
        return track_db.query(track_db).filter(track_db.id.in_(one_export_tracks)).all()

    @classmethod
    def get_exports_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_exports(start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_exports_per_radios(cls):
        exports = cls.session.query(cls).all()
        res = {}
        for export in exports:
            if export.radio_name in res.keys():
                res[export.radio_name].append(export)
            else:
                res[export.radio_name] = [export]
        # cls.session.close()
        return res

    @classmethod
    def get_exports_num_per_radio(cls, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(q_filter=q_filter, between_argument='export_date')

    @classmethod
    def get_exports_num_per_radios(cls):

        radios = [radio[0] for radio in cls.session.query(cls.radio_name).all()]
        res = {}
        for radio in radios:
            res[radio] = res[radio] + 1 if radio in res.keys() else 1

        # cls.session.close()
        return res

    @classmethod
    def get_latest_export_for_radio(cls, radio_name):
        return cls.query(cls).filter(cls.radio_name == radio_name).order_by(cls.export_date.desc()).first()

    @classmethod
    def get_exports_per_date_per_radio(cls, start_date, end_date, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_exports(start_date, end_date, q_filter=q_filter, start=start_id, end=end_id)

    @classmethod
    def get_exports_per_date_per_radio_num(cls, start_date, end_date, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='export_date')

    @classmethod
    def export_radio(cls, radio_name):
        pass

    @classmethod
    def export_imports(cls, imports):
        """
        :param imports:
        :return:
        """
        if not isinstance(imports, list):
            imports = [imports]

        imports_to_export = []
        for one_import in imports:
            if isinstance(one_import, int):
                one_import = tracks_import.TracksImport.query(tracks_import.TracksImport).filter(
                    tracks_import.TracksImport.id == one_import)

            elif isinstance(one_import, datetime):
                one_import = tracks_import.TracksImport.query(tracks_import.TracksImport).filter(
                    tracks_import.TracksImport.import_date == one_import)

            elif isinstance(one_import, dict):
                one_import = tracks_import.TracksImport.query(tracks_import.TracksImport).filter(
                    tracks_import.TracksImport.id == one_import['id'])

            if isinstance(one_import, Query) and one_import.count() == 1:
                one_import = one_import.first()
                one_import.session.close()
                imports_to_export.append(one_import)

                                          #   {'id': one_import.id,
                                          # 'tracks': one_import.get_import_tracks(one_import.import_date),
                                          # 'radio': one_import.radio_name})

        if len(imports_to_export) != len(imports):
            return {'success': False,
                    'result': 'imports count mismatch',
                    'requested': imports,
                    'found': imports_to_export}

        result = []
        success = True
        for one_import in imports_to_export:
            tracks = one_import.get_import_tracks(one_import.import_date)
            account_id = one_import.requester
            radio_name = one_import.radio_name
            import_date = one_import.import_date
            #one_import.session.close()
            res = cls.export_tracks_new(tracks=tracks,
                                        account_id=account_id,
                                        radio_name=radio_name)
            res['import'] = one_import.id
            success = success and res['success']
            if res['success']:
                latest_export = user.User.get_user_exports(one_import.requester)[0]

                cls.update_row({'export_date': latest_export.export_date,
                                'import_id': res['import'] })

                tracks_import.TracksImport.update_row({'import_date': import_date,
                                                       'exported': True})

            result.append(res)

        return {'success': success, 'result': result}

        # # grouping imports by radio name
        # imports_grouped_by_radio = {}
        # for one_import in imports_to_export:
        #     if not imports_grouped_by_radio.get(one_import['radio']):
        #         imports_grouped_by_radio[one_import['radio']] = one_import['tracks']
        #     else:
        #         imports_grouped_by_radio[one_import['radio']].append(one_import['tracks'])
        #
        # result = []
        # for radio in imports_grouped_by_radio:
        #     result.append(cls.export_tracks_new(imports_grouped_by_radio[radio], account_id, radio))
        #
        # return result

    @classmethod
    def export_tracks_new(cls, tracks, account_id, radio_name, service_name='', token=''):
        """
        :param tracks: list of tracks ids or list of dictionaries (list of tracks from DB)
        :param account_id: user account
        :param service_name: user music service
        :param token: token for music service
        :param radio_name: radio name (need to add tracks to specific album); playlist for liked tracks???
        :return:
        """
        if not service_name:
            service_name = user.User.get_user(account_id).service_name
        else:
            service_name = service_name.lower()

        if not token:
            token = session['oauth']['token']

        if not isinstance(tracks, list):
            tracks = [tracks]

        radio_name = radio_name.upper()
        tracks_ids = []
        for one_track in tracks:
            if isinstance(one_track, int):
                one_track = track.Track.query(track.Track).filter(track.Track.id == one_track).first()
                one_track.session.close()
                if one_track and one_track.services.get(service_name):
                    tracks_ids.append(one_track.services.get(service_name))

            elif isinstance(one_track, dict) and one_track['services'].get(service_name):
                tracks_ids.append(one_track['services'].get(service_name))

            elif isinstance(one_track, (track.Track, Query)) and one_track.services.get(service_name):
                tracks_ids.append(one_track.services.get(service_name))
                one_track.session.close()

        ms = ServiceWorker.get_service(service_name, token)
        playlist_name = config.MusicService.DEFAULT_PLAYLIST_NAME + radio_name
        playlist = ms.get_user_playlist_by_name(playlist_name)
        if playlist['success']:
            playlist = playlist['result']['id']
        else:
            playlist = ms.create_playlist(playlist_name)
            if playlist['success']:
                playlist = playlist['result']['id']
            else:
                return {'success': False, 'result': playlist['result']}

        results = ms.add_tracks_by_ids_to_playlist(playlist, tracks_ids)
        if results['success'] and isinstance(results['result'], str):
            tracks_ids = []

        results['export_data'] = {
                                    'export_date': datetime.now(),
                                    'requester': account_id,
                                    'radio_name': radio_name,
                                    'num_tracks_requested': len(tracks),
                                    'num_tracks_added': len(tracks_ids),
                                    'playlist_id': playlist,
                                    'service_name': service_name
                                  }

        if results['success']:
            cls.commit_data(results['export_data'])

        return results
