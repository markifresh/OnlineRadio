from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, Float, Sequence, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.orm import lazyload
from application.db_models import track_db


class DBImport(BaseExtended):
    unique_search_field = 'import_date'

    __tablename__ = 'dbImports'
    id = Column(Integer, primary_key=True)
    import_date = Column(DateTime, Sequence('dbimport_import_date_seq'), unique=True)  # update time in ms
    tracks = relationship('track_db.Track', lazy='dynamic')
    num_tracks_added = Column(Integer, default=0)
    num_tracks_requested = Column(Integer, default=0)
    radio_name = Column(String(20), ForeignKey('radios.name'), nullable=False)
    import_duration = Column(Float, default=0)

    def __repr__(self):
        return f"<dbImport({self.import_date}, {self.radio_name}, " \
               f"{self.num_tracks_added} vs {self.num_tracks_requested})>"

    @classmethod
    def query_imports(cls, start_date='', end_date='', start='', end='', q_filter=''):
        q_selector = cls.query(cls.import_date, cls.radio_name, cls.num_tracks_added)
        res = cls.query_objects(q_selector=q_selector,
                                q_filter=q_filter,
                                start_date=start_date,
                                end_date=end_date,
                                between_argument='import_date')
        res = cls.limit_objects(res, start, end).all()

        return [{'import_date': imp[0], 'radio_name': imp[1], 'num_tracks_added': imp[2]} for imp in res]

    @classmethod
    def get_imports_num(cls):
        return cls.query_objects_num()

    @classmethod
    def get_import_by_date(cls, import_date):
        if isinstance(import_date, str):
            import_date = datetime.strptime(import_date, '%Y-%m-%dT%H:%M:%S.%f')

        q_filter = cls.import_date == import_date
        return cls.query_objects(q_filter=q_filter).one_or_none()

    @classmethod
    def get_imports_per_date(cls, start_date, end_date, start_id='', end_id=''):
        return cls.query_imports(start_date=start_date, end_date=end_date, start=start_id, end=end_id)

    @classmethod
    def get_imports_per_date_num(cls, start_date, end_date):
        return cls.query_objects_num(start_date, end_date, between_argument='import_date')

    @classmethod
    def get_imports_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_exports(start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_imports_per_radios(cls):
        imports = cls.session.query(cls).all()
        res = {}
        for db_import in imports:
            if db_import.radio_name in res.keys():
                res[db_import.radio_name].append(db_import)
            else:
                res[db_import.radio_name] = [db_import]
        cls.session.close()
        return res

    @classmethod
    def get_imports_num_per_radio(cls, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(q_filter=q_filter, between_argument='import_date')

    @classmethod
    def get_imports_num_per_radios(cls):
        from application.db_models.radio_db import Radio
        init_dict = {radio.name: 0 for radio in Radio.all()}
        return cls.query_objects_num_all_sorted(sort_argument='radio_name',
                                                init_dict=init_dict)

    @classmethod
    def get_latest_import_for_radio(cls, radio_name):
        return cls.query(cls).filter(cls.radio_name == radio_name).order_by(cls.import_date.desc()).first()

    @classmethod
    def get_imports_per_date_per_radio(cls, start_date, end_date, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_imports(start_date, end_date, q_filter=q_filter, start=start_id, end=end_id)

    @classmethod
    def get_imports_per_date_per_radio_num(cls, start_date, end_date, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='import_date')
