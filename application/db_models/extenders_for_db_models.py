from . import set_session
from sqlalchemy import desc
from sqlalchemy.orm import query
from sqlalchemy.ext.declarative import api
from traceback import format_exc as traceback_format_exc
# from application.db_models import db_session, engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList
from datetime import datetime, timedelta


Base = declarative_base()

class BaseExtended(Base):

    unique_search_field = ''
    __abstract__ = True

    session = set_session()

    engine = session.bind
    query = session.query

    @classmethod
    def all(cls, sort_by='', reverse=False):
        if sort_by and reverse:
            res = cls.session.query(cls).order_by(desc(getattr(cls, sort_by))).all()

        elif sort_by and not reverse:
            res = cls.session.query(cls).order_by(getattr(cls, sort_by)).all()

        else:
            res = cls.session.query(cls).all()

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


        res = []
        col_names = db_objects[0].__table__.columns.keys()
        # prime_key = cls.__table__.primary_key.columns.values()[0].name

        for db_object in db_objects:
            obj = {}
            for col_name in col_names:
                obj[col_name] = getattr(db_object, col_name)
            res.append(obj)

        return res

    @classmethod
    def update_row(cls, data, create_new=False):

        # if call from class
        if isinstance(cls, api.DeclarativeMeta):
            if cls.unique_search_field not in data.keys():
                return {'success': False, 'result': 'Missing filter_id argument'}
            obj = cls.query(cls).filter(getattr(cls, cls.unique_search_field) == data[cls.unique_search_field])

        # if call from object
        else:
            attr = getattr(cls, cls.unique_search_field)
            obj = cls.query(cls).filter(attr == (getattr(cls, cls.unique_search_field)))

        if obj.count() == 1:
            try:
                obj.update(data)
                cls.session.commit()
                result = {'success': True, 'result': data}
            except:
                cls.session.rollback()
                result = {'success': False, 'result': traceback_format_exc()}

        elif obj.count() == 0 and create_new:
            return cls.commit_data(data)

        else:
            result = {'success': False, 'result': f'Instead of 1 object - {obj.count()} object was found'}

        # cls.session.close()
        return result

    @classmethod
    def commit_data(cls, data):
        new_obj = None

        if isinstance(data, list) or isinstance(data, tuple):
            cls.session.add_all(data)
        else:
            if isinstance(data, dict):
                new_obj = cls(**data)
            else:
                new_obj = data

        try:
            cls.session.add(new_obj)
            cls.session.commit()
            result = {'success': True, 'result': data, 'id': new_obj.id if new_obj else None}
        except:
            cls.session.rollback()
            result = {'success': False, 'result': traceback_format_exc()}

        # cls.session.close()
        return result

    # @classmethod
    # def check_prepare_date_input(cls, start_date, end_date):
    #     if not (isinstance(start_date, str) == isinstance(end_date, str) == True):
    #         return False, 'Wrong Type format'
    #
    #     if not ('-' in start_date and '-' in end_date):
    #         return False, 'Wrong Format'
    #
    #     start_day = int(start_date.split('-')[0])
    #     end_day = int(end_date.split('-')[0])
    #     print(start_day, end_day)
    #     if end_day - start_day < 1:
    #         return False, 'difference in days less than 1'
    #     start_date = start_date.replace('-', '/')
    #     end_date = end_date.replace('-', '/')
    #
    #     return True, {'start_date': start_date, 'end_date': end_date}

    @classmethod
    def limit_objects(cls, query_res, start_id='', end_id=''):
        start_id = 0 if not start_id else start_id
        end_id = 50 if not end_id else end_id
        return query_res.offset(start_id).limit(end_id)


    @classmethod
    def query_objects(cls, q_selector='', start_date='', end_date='',  q_filter='', between_argument=''):
        res = cls.query(cls) if not q_selector else q_selector

        if isinstance(q_filter, (BinaryExpression, BooleanClauseList)):
            res = res.filter(q_filter)

        if start_date and end_date:
            res = res.filter(getattr(cls, between_argument).between(start_date, end_date))

        return res

    @classmethod
    def query_objects_num(cls, start_date='', end_date='', q_filter='', between_argument=''):
        """ Returns number of objects for specific filter and date range
        start_date (datetime): from this date
        end_date (datetime): till this date

        between_argument (str): column name to select 'date_range' from
        (for example: 'db_import_date' - will apply: .filter(cls.db_import_date.between(start, end)))

        q_filter (BinaryExpression): query condition
        (for example: cls.radio_name == radio_name)

        """
        res = cls.query(cls.id)


        if isinstance(q_filter, (BinaryExpression, BooleanClauseList)):
            res = res.filter(q_filter)

        if start_date and end_date:
            res = res.filter(getattr(cls, between_argument).between(start_date, end_date))

        return {'number': res.count()}

    @classmethod
    def query_objects_num_all_sorted(cls, start_date='', end_date='', between_argument='', sort_argument='',
                                     init_dict={}, q_filter=''):
        res = init_dict
        sorting_objects = cls.query(getattr(cls, sort_argument))

        if isinstance(q_filter, (BinaryExpression, BooleanClauseList)):
            sorting_objects = sorting_objects.filter(q_filter)

        if start_date and end_date:
            sorting_objects = sorting_objects.filter(getattr(cls, between_argument).between(start_date, end_date))

        sorting_objects = [sort_obj[0] for sort_obj in sorting_objects.all()]
        for sort_obj in sorting_objects:
            res[sort_obj] = res[sort_obj] + 1 if sort_obj in res.keys() else 1

        return res

    @classmethod
    def create_tables(cls):
        cls.metadata.create_all(cls.engine)

    @classmethod
    def drop_table(cls):
        cls.__table__.drop(cls.engine)

    @classmethod
    def rebuild_table(cls):
        cls.drop_table()
        cls.create_tables()
