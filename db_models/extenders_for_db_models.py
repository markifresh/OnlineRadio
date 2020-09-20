import config
from sqlalchemy.orm import query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import api
from sqlalchemy import create_engine
from traceback import format_exc as traceback_format_exc


Base = declarative_base()

class BaseExtended(Base):
    unique_search_field = ''

    __abstract__ = True

    Base.metadata.bind = create_engine(f'sqlite:///{config.db_location}', echo=True)

    @classmethod
    def create_db_session(cls):
        from app import db
        return db.session


    @classmethod
    def get_all_objects(cls):
        db_session = cls.create_db_session()
        res = db_session.query(cls).all()
        db_session.close()
        return res

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
        session = self.create_db_session()

        # if call from class
        if isinstance(self, api.DeclarativeMeta):
            if not filter_id:
                return {'success': False, 'result': 'Missing filter_id argument'}
            obj = session.query(self).filter(getattr(self, self.unique_search_field) == filter_id)

        # if call from class
        else:
            attr = getattr(self.__class__, self.unique_search_field)
            obj = session.query(self.__class__).filter(attr == (getattr(self, self.unique_search_field)))

        if obj.count() == 1:
            try:
                obj.update(data)
                session.commit()
                result = {'success': True, 'result': ''}
            except:
                result = {'success': False, 'result': traceback_format_exc()}

        else:
            result = {'success': False, 'result': f'Instead of 1 - {obj.count()} object was found'}

        session.close()
        return result

    @classmethod
    def commit_data(cls, data, session=''):
        if not session:
            session = cls.create_db_session()
        if isinstance(data, list) or isinstance(data, tuple):
            session.add_all(data)
        else:
            session.add(data)

        try:
            session.commit()
            result = {'success': True, 'result': data}
        except:
            session.rollback()
            result = {'success': False, 'result': traceback_format_exc()}

        session.close()
        return result

    @staticmethod
    def create_tables():
        engine = create_engine(f'sqlite:///{config.db_location}', echo=True)
        Base.metadata.create_all(engine)