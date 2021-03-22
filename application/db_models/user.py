from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class User(UserMixin, BaseExtended):

    __tablename__ = 'login-users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=False)
    email = Column(String(40), unique=True, nullable=False)
    password = Column(String(200), primary_key=False, unique=False, nullable=False)
    created_on = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, index=False, unique=False, nullable=True)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.name}>'
