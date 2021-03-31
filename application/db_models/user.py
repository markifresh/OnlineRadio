from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime

class User(UserMixin, BaseExtended):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime(), default=datetime.now)
    accounts = Column(JSON)
    last_login = Column(DateTime)

    @classmethod
    def get_user_id(cls, session_dict):
        ms_service = session_dict['ms_service']
        ms_username = session_dict['ms_user']['display_name']
        ms_user_id = session_dict['ms_user']['id']
        db_user = cls.query(cls).filter(cls.accounts.contains({ms_service: {
                  'display_name': ms_username,
                  'id': ms_user_id}}))

        if db_user.count() == 0:
            cls.commit_data({
                'accounts': {
                    ms_service: {
                        'display_name': ms_username,
                        'id': ms_user_id,
                        'last_login': datetime.now()
                    }}})

        # todo: replace update with working one
        elif db_user.count() == 1:
            db_user.update({'last_login': datetime.now()})

        else:
            return {'success': False, 'result': 'few matches'}

        return {'success': True, 'result': ''}

    # def set_password(self, password):
    #     """Create hashed password."""
    #     self.password = generate_password_hash(password, method='sha256')
    #
    # def check_password(self, password):
    #     """Check hashed password."""
    #     return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.id}>'
