from . import create_db
from config import DevConfig
from sqlalchemy.orm import query
from sqlalchemy.ext.declarative import api
from traceback import format_exc as traceback_format_exc
# from application.db_models import db_session, engine
from flask import current_app
from sqlalchemy.ext.declarative import declarative_base

default_config = DevConfig
Base = declarative_base()

class BaseExtended(Base):
    def __init__(self, session=''):
        self.set_session(session)

    unique_search_field = ''
    __abstract__ = True

    if getattr(current_app, 'session', ''):
        engine = current_app.session.bind
        session = current_app.session

    # else:
    #     session = create_db(DevConfig)()
    #     engine = session.bind

    @classmethod
    def set_session(cls, config_class, session=create_db):
        cls.session = session(config_class)
        cls.engine = cls.session.bind
        cls.query = cls.session.query

    @classmethod
    def all(cls):
        return cls.session.query(cls).all()

    @classmethod
    def to_json(cls, db_objects):
        prime_key = cls.unique_search_field
        if isinstance(db_objects, query.Query):
            db_objects = db_objects.all()

        elif isinstance(db_objects, cls):
            db_objects = [db_objects]

        if not isinstance(db_objects, list) or len(db_objects) == 0:
            return {}


        res = {}
        col_names = db_objects[0].__table__.columns.keys()
        # prime_key = cls.__table__.primary_key.columns.values()[0].name

        for db_object in db_objects:
            obj = {}
            for col_name in col_names:
                obj[col_name] = getattr(db_object, col_name)
            res[getattr(db_object, prime_key)] = obj

        return res

    def update_row(self, data, filter_id=''):

        # if call from class
        if isinstance(self, api.DeclarativeMeta):
            if not filter_id:
                return {'success': False, 'result': 'Missing filter_id argument'}
            obj = self.session.query(self).filter(getattr(self, self.unique_search_field) == filter_id)

        # if call from class
        else:
            attr = getattr(self.__class__, self.unique_search_field)
            obj = self.session.query(self.__class__).filter(attr == (getattr(self, self.unique_search_field)))

        if obj.count() == 1:
            try:
                obj.update(data)
                self.session.commit()
                result = {'success': True, 'result': ''}
            except:
                result = {'success': False, 'result': traceback_format_exc()}

        else:
            result = {'success': False, 'result': f'Instead of 1 - {obj.count()} object was found'}

        self.session.close()
        return result

    @classmethod
    def commit_data(cls, data):

        if isinstance(data, list) or isinstance(data, tuple):
            cls.session.add_all(data)
        else:
            cls.session.add(data)

        try:
            cls.session.commit()
            result = {'success': True, 'result': data}
        except:
            cls.session.rollback()
            result = {'success': False, 'result': traceback_format_exc()}

        cls.session.close()
        return result

    @staticmethod
    def create_tables():
        Base.metadata.create_all(engine)