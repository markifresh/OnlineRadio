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

class User(UserMixin, BaseExtended):
    unique_search_field = 'account_id'

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(), default=datetime.now)
    service_name = Column(String)
    display_name = Column(String)
    account_id = Column(Integer)
    account_uri = Column(String, unique=True)
    last_login = Column(DateTime)
    settings = Column(JSON)     # export liked automatically to service
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
        result = None
        res = cls.query(cls).filter(cls.account_id == account_id)

            # cls.account_id,
            # cls.account_uri,
            # cls.created_on,
            # cls.display_name,
            # cls.last_login,
            # cls.service_name,
            # cls.settings

        if res.count() == 1:
            result = res.first()

        return result

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
        imports = cls.get_user_imports(account_id)
        track_db = track.Track
        for one_import in imports:
            one_import_tracks = one_import.tracks.split(',')
            tracks.append(track_db.query(track_db).filter(track_db.id.in_(one_import_tracks)).all())
        return tracks


    # def get_tracks(self):
    #     return self.get_user_tracks(self.account_id)

    @classmethod
    def get_user_liked_tracks(cls, account_id):
        user = cls.get_user(account_id)
        tracks_list = user.liked_tracks[:-1].split(',')
        track_db = track.Track
        return track_db.query(track_db).filter(track_db.id.in_(tracks_list)).all()

    # def get_liked_tracks(self):
    #     return self.get_user_liked_tracks(self.account_id)

    @classmethod
    def get_user_imports(cls, account_id):
        user = cls.get_user(account_id)
        res = user.imports.order_by(desc(tracks_import.TracksImport.id)).all()
        user.session.close()
        return res

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
        exports = cls.get_user_exports(account_id)
        track_db = track.Track
        for one_export in exports:
            one_export_tracks = one_export.tracks.split(',')
            tracks.append(track_db.query(track_db).filter(track_db.id.in_(one_export_tracks)).all())
        return tracks

    # def get_exported_tracks(self):
    #     return self.get_user_exported_tracks(self.account_id)


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
        for record in imports:
            if radios.get(record.radio_name):
                radios[record.radio_name]['num_imported'] += record.num_tracks_added
                if not radios[record.radio_name].get('latest_import'):
                    radios[record.radio_name]['latest_import'] = record.import_date

        exports = cls.get_user_exports(account_id)
        for record in exports:
            if radios.get(record.radio_name):
                radios[record.radio_name]['num_exported'] += record.num_tracks_added
                if not radios[record.radio_name].get('latest_export'):
                    radios[record.radio_name]['latest_import'] = record.export_date

        for radio in radios:
            radios[radio]['num_to_export'] = radios[radio]['num_imported'] - radios[radio]['num_exported']

        return radios


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


