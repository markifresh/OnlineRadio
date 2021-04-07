from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from application.db_models import tracks_import
from application.db_models import tracks_export

class User(UserMixin, BaseExtended):
    unique_search_field = 'account_uri'

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


