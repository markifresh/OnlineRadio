from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, DateTime, JSON, desc
from sqlalchemy.orm import relationship
from datetime import datetime
from application.db_models import tracks_import
from application.db_models import tracks_export
from application.db_models import radio
from application.db_models import track
from application.CustomExceptions import UniqueDBObjectError, BasicCustomException
from application.schema_models import validators
from config import users_settings, date_format

class User(UserMixin, BaseExtended):
    unique_search_field = 'account_id'

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(), default=datetime.now)
    service_name = Column(String)
    display_name = Column(String)
    account_id = Column(String)
    account_uri = Column(String, unique=True)
    last_login = Column(DateTime)
    settings = Column(String)     # export liked automatically to service
    radios = Column(String)
    liked_tracks = Column(String)
    exports = relationship('tracks_export.TracksExport', lazy='dynamic')
    imports = relationship('tracks_import.TracksImport', lazy='dynamic')
    # num_tracks = Column(Integer)
    # num_tracks_exported = Column(Integer)


    # todo: method / hybrid attribute for liked tracks - returns a list?
    # todo: the same for radios
    # todo: the same for all exported tracks
    # todo: the same for all imported tracks
    # todo: method to get user by json (classmethod)
    # todo: method to add tracks
    # todo: method to add/set radios

    @classmethod
    def get_all_users(cls, start_id=0, end_id=50):
        return cls.query(cls).filter(cls.id.between(start_id, end_id)).all()
        # cls.session.close()
        # return [{'account_id': user[0],
        #          'created_on': user[1],
        #          'display_name': user[2],
        #          'service_name': user[3],
        #          } for user in users]


    @classmethod
    def get_user(cls, account_id):
    # account_id in format "<ms_service>:<account_id>"
        res = cls.query(cls).filter(cls.account_id == account_id)

            # cls.account_id,
            # cls.account_uri,
            # cls.created_on,
            # cls.display_name,
            # cls.last_login,
            # cls.service_name,
            # cls.settings
        objects_count = res.count()
        if objects_count != 1:
            raise UniqueDBObjectError(account_id, objects_count, cls.__name__)

        return res.first()


    @classmethod
    def user_update(cls, update_dict):
        res = cls.update_row(update_dict)
        if res['success']:
            res = cls.get_user(update_dict['account_id'])
        return res

    @classmethod
    def get_user_radios(cls, account_id):
        user = cls.get_user(account_id)
        if not user.radios:
            return []
        radios_list = user.radios[:-1].split(',')
        #return radio.Radio.get_radios_by_name(radios_list)
        return radio.Radio.query(radio.Radio).filter(radio.Radio.name.in_(radios_list)).all()

    # def get_radios(self):
    #     return self.get_user_radios(self.account_id)

    # @classmethod
    # def get_user_tracks(cls, account_id):
    #     user = cls.get_user(account_id)
    #     tracks_list = user.tracks[:-1].split(',')
    #     track_db = track.Track
    #     return track_db.query(track_db).filter(track_db.id.in_(tracks_list)).all()

    @classmethod
    def get_user_tracks(cls, account_id):
        tracks = []
        imports_db = tracks_import.TracksImport
        imports = cls.get_user_imports(account_id)
        for one_import in imports:
            tracks.append(imports_db.get_import_tracks(one_import.import_date))
        return tracks


    # def get_tracks(self):
    #     return self.get_user_tracks(self.account_id)

    @classmethod
    def get_user_liked_tracks(cls, account_id):
        user = cls.get_user(account_id)
        tracks_list = []

        if user.liked_tracks:
            tracks_list = user.liked_tracks.split(',')
            track_db = track.Track
            tracks_list = track_db.query(track_db).filter(track_db.id.in_(tracks_list)).all()

        return tracks_list

    # def get_liked_tracks(self):
    #     return self.get_user_liked_tracks(self.account_id)

    @classmethod
    def liked_tracks_add(cls, account_id, tracks_ids_list):
        if not isinstance(tracks_ids_list, list):
            tracks_ids_list = [tracks_ids_list]

        # get a list
        tracks_ids_list = [int(one_track) for one_track in tracks_ids_list]

        # verify all tracks in DB
        track_db = track.Track
        tracks = track_db.query(track_db).filter(track_db.id.in_(tracks_ids_list)).all()
        track_db.session.close()

        if len(tracks_ids_list) != len(tracks):
            found = [tr.id for tr in tracks]
            missing = [tr for tr in tracks_ids_list if tr not in found]
            raise BasicCustomException(f'Could not find tracks: {missing}')

        # get users liked tracks and check new tracks not in liked tracks already
        user = cls.get_user(account_id)
        tracks_ids_list = [str(one_track) for one_track in tracks_ids_list]
        user_list = [] if not user.liked_tracks else user.liked_tracks.split(',')

        for new_track in tracks_ids_list:
            if new_track in user_list:
                raise BasicCustomException(f'{new_track} is already in list of liked')

        user_list = user_list + tracks_ids_list
        user_list = ','.join(user_list)

        db_update = cls.update_row({'account_id': account_id, 'liked_tracks': user_list})
        if not db_update['success']:
            raise BasicCustomException(f'Failed to update user DB object \n {db_update}')

        return tracks

    @classmethod
    def liked_tracks_remove(cls, account_id, tracks_ids_list):
        if not isinstance(tracks_ids_list, list):
            tracks_ids_list = [tracks_ids_list]

        tracks_ids_list = [int(one_track) for one_track in tracks_ids_list]
        track_db = track.Track
        tracks = track_db.query(track_db).filter(track_db.id.in_(tracks_ids_list)).all()
        track_db.session.close()

        if len(tracks_ids_list) != len(tracks):
            found = [tr.id for tr in tracks]
            missing = [tr for tr in tracks_ids_list if tr not in found]
            raise BasicCustomException(f'Could not find tracks: {missing}')


        tracks_ids_list = [str(one_track) for one_track in tracks_ids_list]
        user = cls.get_user(account_id)
        user_list = [] if not user.liked_tracks else user.liked_tracks.split(',')

        removed_tracks = []
        for one_track in tracks_ids_list:
            if one_track in user_list:
                user_list.remove(one_track)
                removed_tracks.append(one_track)

        user_list = ','.join(user_list)

        db_update = cls.update_row({'account_id': account_id, 'liked_tracks': user_list})
        if not db_update['success']:
            raise BasicCustomException(f'Failed to update user DB object \n {db_update}')

        return tracks


    @classmethod
    def get_user_imports(cls, account_id):
        user = cls.get_user(account_id)
        res = user.imports.order_by(desc(tracks_import.TracksImport.id)).all()
        for i in range(len(res)):
            if res[i].related_to:
                parent = tracks_import.TracksImport.query(tracks_import.TracksImport).\
                    filter(tracks_import.TracksImport.id == res[i].related_to).first()
                orig_import = res[i]
                res[i] = parent
                res[i].id = orig_import.id
                res[i].requester = orig_import.requester
                res[i].import_date = orig_import.import_date
                res[i].exported = orig_import.exported
        user.session.close()
        return res

    @classmethod
    def get_user_import(cls, account_id, import_date):
        user = cls.get_user(account_id)
        return user.imports.filter(tracks_import.TracksImport.import_date == validators.validate_date(import_date)).first()

    @classmethod
    def export_tracks(cls, account_id, track_ids, radio_name):
        if not isinstance(track_ids, list):
            track_ids = [track_ids]

        track_ids = [int(one_track) for one_track in track_ids]
        track_db = track.Track
        tracks = track_db.query(track_db).filter(track_db.id.in_(track_ids)).all()
        track_db.session.close()

        export_db = tracks_export.TracksExport
        res = export_db.export_tracks_new(track_ids, account_id, radio_name)
        export_db.session.close()
        if res['success']:
            return tracks

        raise BasicCustomException(f'Failed to export tracks: \n {str(res)}')

    @classmethod
    def import_tracks_remove(cls, account_id, import_date, track_ids):
        if not isinstance(track_ids, list):
            track_ids = [track_ids]

        requested_import = cls.get_user_import(account_id, import_date)
        tracks = requested_import.tracks.split(', ')

        for one_track in track_ids:
            if one_track in tracks:
                tracks.remove(one_track)
            else:
                raise BasicCustomException(f'Track: {one_track} not in import: {import_date}')

        tracks = ', '.join(tracks)
        res = tracks_import.TracksImport.update_row({'import_date': validators.validate_date(import_date), 'tracks': tracks})

        if not res['success']:
            raise BasicCustomException(str(res))

        track_db = track.Track
        removed_tracks = [int(one_track) for one_track in track_ids]
        removed_track = track_db.query(track_db).filter(track_db.id.in_(removed_tracks)).all()
        track_db.session.close()
        return removed_track


    # def get_imports(self):
    #     return self.get_user_imports(self.account_id)

    @classmethod
    def get_user_exports(cls, account_id):
        user = cls.get_user(account_id)
        res = user.exports.order_by(desc(tracks_export.TracksExport.id)).all()
        user.session.close()
        return res

    # def get_exports(self):
    #     return self.get_user_exports(self.account_id)

    @classmethod
    def get_user_exported_tracks(cls, account_id):
        tracks = []
        export_db = tracks_export.TracksExport
        exports = cls.get_user_exports(account_id)
        for one_export in exports:
            tracks.append(export_db.get_export_tracks(one_export.export_date))
        return tracks

    # def get_exported_tracks(self):
    #     return self.get_user_exported_tracks(self.account_id)

    @classmethod
    def get_user_unexported_imports(cls, account_id):
        user = cls.get_user(account_id)
        return user.imports.filter(tracks_import.TracksImport.exported == False).all()

    @classmethod
    def get_user_unexported_imports_by_radio(cls, account_id, radio_name):
        user = cls.get_user(account_id)
        return user.imports.filter(tracks_import.TracksImport.exported == False,
                                   tracks_import.TracksImport.radio_name == radio_name).all()

    @classmethod
    def get_user_not_exported_tracks(cls, account_id):
        exported_tracks = cls.get_user_exported_tracks(account_id)
        imported_tracks = cls.get_user_tracks(account_id)
        return [track_obj for track_obj in imported_tracks if track_obj not in exported_tracks]

    # def get_not_exported_tracks(self):
    #     return self.get_user_not_exported_tracks(self.account_id)

    @classmethod
    def get_user_tracks_num_imported(cls, account_id):
        tracks_imported = 0
        imports = cls.get_user_imports(account_id)
        for one_import in imports:
            tracks_imported += one_import.num_tracks_added
        return tracks_imported

    # def get_tracks_num_imported(self):
    #     return self.get_user_tracks_num_imported()

    @classmethod
    def get_user_tracks_num_exported(cls, account_id):
        tracks_exported = 0
        exports = cls.get_user_exports(account_id)
        for one_export in exports:
            tracks_exported += one_export.num_tracks_added
        return tracks_exported

    # def get_tracks_num_exported(self):
    #     return self.get_user_tracks_num_imported()

    @classmethod
    def get_user_tracks_num_not_exported(cls, account_id):
        return cls.get_user_tracks_num_imported(account_id) - cls.get_user_tracks_num_exported(account_id)

    # def get_tracks_num_not_exported(self):
    #     return self.get_user_tracks_num_not_exported(self.account_id)

    @classmethod
    def get_user_radio_page_data(cls, account_id):
        radios = cls.to_json(cls.get_user_radios(account_id))
        radios = {radio['name']: radio for radio in radios}
        for radio in radios:
            radios[radio]['num_imported'] = 0
            radios[radio]['num_exported'] = 0

        imports = cls.get_user_imports(account_id)
        for one_import in imports:
            radio_name = one_import.radio_name
            if radios.get(radio_name):
                radios[radio_name]['num_imported'] += one_import.num_tracks_added
                if one_import.exported:
                    radios[radio_name]['num_exported'] += one_import.num_tracks_added
                if not radios[one_import.radio_name].get('latest_import'):
                    radios[one_import.radio_name]['latest_import'] = one_import.import_date

        exports = cls.get_user_exports(account_id)
        for one_export in exports:
            if radios.get(one_export.radio_name):
                if not radios[one_export.radio_name].get('latest_export'):
                    radios[one_export.radio_name]['latest_export'] = one_export.export_date

        for radio in radios:
            radios[radio]['num_to_export'] = radios[radio]['num_imported'] - radios[radio]['num_exported']

        return radios


    @classmethod
    def get_user_imports_for_radio(cls, account_id, radio_name):
        radio_imports = []
        user_imports = cls.get_user_imports(account_id)
        for user_import in user_imports:
            if user_import.radio_name == radio_name:
                radio_imports.append(user_import)
        return radio_imports

    @classmethod
    def get_user_imported_tracks_for_radio(cls, account_id, radio_name):
        tracks = []
        imports_db = tracks_import.TracksImport
        imports = cls.get_user_imports_for_radio(account_id, radio_name)
        for one_import in imports:
            tracks.append(imports_db.get_import_tracks(one_import.import_date))
        return tracks

    @classmethod
    def get_user_exports_for_radio(cls, account_id, radio_name):
        radio_exports = []
        user_exports = cls.get_user_exports(account_id)
        for user_export in user_exports:
            if user_export.radio_name == radio_name:
                radio_exports.append(user_export)
        return radio_exports

    @classmethod
    def get_user_exported_tracks_for_radio(cls, account_id, radio_name):
        tracks = []
        exports_db = tracks_export.TracksExport
        exports = cls.get_user_exports_for_radio(account_id, radio_name)
        for one_export in exports:
            tracks.append(exports_db.get_export_tracks(one_export.export_date))
        return tracks

    @classmethod
    def add_user_radio(cls, account_id, radio_name):
        radios = [radio_obj.name for radio_obj in cls.get_user_radios(account_id)]

        if radio_name in radios:
            raise BasicCustomException(f'radio "{radio_name}" already in user radios')

        radios.append(radio_name)
        radios_str = ''
        for radio_str in radios:
            radios_str += radio_str + ','

        result = cls.update_row({'radios': radios_str, 'account_id': account_id})
        result['radio_name'] = radio_name

        return result

    @classmethod
    def delete_user_radio(cls, account_id, radio_name):
        radios = [radio_obj.name for radio_obj in cls.get_user_radios(account_id)]

        if radio_name not in radios:
            raise BasicCustomException(f'radio "{radio_name}" not in user radios')

        radios.remove(radio_name)
        radios_str = ''
        for radio_str in radios:
            radios_str += radio_str + ','
        result = cls.update_row({'radios': radios_str, 'account_id': account_id})
        result['radio_name'] = radio_name
        return result

    @classmethod
    def get_user_settings(cls, account_id):
        settings = cls.get_user(account_id).settings
        if not settings:
            return []
        else:
            return settings[:-1].split(',')

    @classmethod
    def add_user_setting(cls, account_id, setting):
        user_settings = cls.get_user_settings(account_id)

        if setting in user_settings:
            raise BasicCustomException(f'setting "{setting}" already in user settings')

        user_settings.append(setting)
        settings_str = ''
        for user_setting in user_settings:
            settings_str += user_setting + ','

        result = cls.update_row({'settings': settings_str, 'account_id': account_id})
        result['setting'] = setting
        return result

    @classmethod
    def delete_user_setting(cls, account_id, setting):
        user_settings = cls.get_user_settings(account_id)

        if setting not in user_settings:
            raise BasicCustomException(f'setting "{setting}" not in user settings')

        user_settings.remove(setting)
        settings_str = ''
        for user_setting in user_settings:
            settings_str += user_setting + ','

        result = cls.update_row({'settings': settings_str, 'account_id': account_id})
        result['setting'] = setting
        return result

    # @classmethod
    # def get_user_import_

    # @classmethod
    # def get_user_id(cls, session_dict):
    #     ms_service = session_dict['ms_service']
    #     ms_username = session_dict['ms_user']['display_name']
    #     ms_user_id = session_dict['ms_user']['id']
    #     db_user = cls.query(cls).filter(cls.accounts.contains({ms_service: {
    #               'display_name': ms_username,
    #               'id': ms_user_id}}))
    #
    #     if db_user.count() == 0:
    #         cls.commit_data({
    #             'accounts': {
    #                 ms_service: {
    #                     'display_name': ms_username,
    #                     'id': ms_user_id,
    #                     'last_login': datetime.now()
    #                 }}})
    #
    #     # todo: replace update with working one
    #     elif db_user.count() == 1:
    #         db_user.update({'last_login': datetime.now()})
    #
    #     else:
    #         return {'success': False, 'result': 'few matches'}
    #
    #     return {'success': True, 'result': ''}

    # def set_password(self, password):
    #     """Create hashed password."""
    #     self.password = generate_password_hash(password, method='sha256')
    #
    # def check_password(self, password):
    #     """Check hashed password."""
    #     return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.display_name} - {self.service_name}>'


