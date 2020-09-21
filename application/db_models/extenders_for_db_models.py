from sqlalchemy.orm import query
from sqlalchemy.ext.declarative import api
from traceback import format_exc as traceback_format_exc
from application.db_models import db_session, engine, Base


class BaseExtended(Base):
    def __init__(self, session=''):
        self.set_session(session)

    unique_search_field = ''
    __abstract__ = True

    Base.metadata.bind = engine

    @classmethod
    def set_session(cls, session=None):
        if not session:
            cls.session = db_session()
        else:
            cls.session = session
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