from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, DateTime, JSON
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
    tracks = Column(String)
    liked_tracks = Column(String)
    reviewed_tracks = Column(String)
    exports = relationship('tracks_export.TracksExport', lazy='dynamic')
    imports = relationship('tracks_import.TracksImport', lazy='dynamic')

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

        cls.session.close()
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
        radios_list = user.radios[:-1].split(',')
        #return radio.Radio.get_radios_by_name(radios_list)
        return radio.Radio.query(radio.Radio).filter(radio.Radio.name.in_(radios_list)).all()

    def get_radios(self):
        return self.get_user_radios(self.account_id)

    @classmethod
    def get_user_tracks(cls, account_id):
        user = cls.get_user(account_id)
        tracks_list = user.tracks[:-1].split(',')
        track_db = track.Track
        return track_db.query(track_db).filter(track_db.id.in_(tracks_list)).all()

    def get_tracks(self):
        return self.get_user_tracks(self.account_id)

    @classmethod
    def get_user_liked_tracks(cls, account_id):
        user = cls.get_user(account_id)
        tracks_list = user.liked_tracks[:-1].split(',')
        track_db = track.Track
        return track_db.query(track_db).filter(track_db.id.in_(tracks_list)).all()

    def get_liked_tracks(self):
        return self.get_user_liked_tracks(self.account_id)

    @classmethod
    def get_user_imports(cls, account_id):
        user = cls.get_user(account_id)
        return user.imports.all()

    def get_imports(self):
        return self.get_user_imports(self.account_id)

    @classmethod
    def get_user_exports(cls, account_id):
        user = cls.get_user(account_id)
        return user.exports.all()

    def get_exports(self):
        return self.get_user_exports(self.account_id)

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


