from sqlalchemy import Column, Integer, String, Float, Sequence, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import lazyload
from datetime import datetime, timedelta

from application.workers.ExtraFunc import get_date_range_list
from application.db_models.extenders_for_db_models import BaseExtended
from application.db_models import track
from application.db_models import user


class TracksImport(BaseExtended):
    unique_search_field = 'import_date'

    __tablename__ = 'tracksImports'
    id = Column(Integer, primary_key=True)
    import_date = Column(DateTime, Sequence('tracksImport_import_date_seq'), unique=True)  # update time in ms
    tracks = Column(String)
    num_tracks_added = Column(Integer, default=0)
    num_tracks_requested = Column(Integer, default=0)
    radio_name = Column(String(20), ForeignKey('radios.name'), nullable=False)
    import_duration = Column(Float, default=0)
    for_date = Column(DateTime)  # update_time in ms
    type = Column(String)  # full_day / specific_time
    requester = Column(String(20), ForeignKey('users.account_uri'), nullable=False)
    # ? service_name = Column(String)

    def __repr__(self):
        return f"<dbImport({self.import_date}, {self.radio_name}, " \
               f"{self.num_tracks_added} vs {self.num_tracks_requested})>"

    # todo: method to get tracks per import

    @classmethod
    def query_imports(cls, start_date='', end_date='', start='', end='', q_filter=''):
        q_selector = cls.query(cls.import_date, cls.radio_name, cls.num_tracks_added).order_by(cls.import_date.desc())
        res = cls.query_objects(q_selector=q_selector,
                                q_filter=q_filter,
                                start_date=start_date,
                                end_date=end_date,
                                between_argument='import_date')
        res = cls.limit_objects(res, start, end).all()

        return [{'import_date': imp[0].strftime('%Y-%m-%d %H:%M:%S'),
                 'radio_name': imp[1],
                 'num_tracks_added': imp[2] if imp[2] else 0} for imp in res]

    @classmethod
    def get_imports(cls, start_id='', end_id=''):
        return cls.query_imports(start=start_id, end=end_id)


    @classmethod
    def get_imports_num(cls):
        return cls.query_objects_num()

    @classmethod
    def get_import_by_date(cls, import_date):
        if isinstance(import_date, str):
            import_date = datetime.strptime(import_date, '%Y-%m-%dT%H:%M:%S.%f')
        return cls.query(cls).filter(cls.import_date == import_date).one_or_none()

    @classmethod
    def get_import_tracks(cls, import_date):
        one_import = cls.get_import_by_date(import_date)
        track_db = track.Track
        one_import_tracks = one_import.tracks.split(',')
        return track_db.query(track_db).filter(track_db.id.in_(one_import_tracks)).all()

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
        # cls.session.close()
        return res

    @classmethod
    def get_imports_num_per_radio(cls, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(q_filter=q_filter, between_argument='import_date')

    @classmethod
    def get_imports_num_per_radios(cls):
        from application.db_models.radio import Radio
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

    @classmethod
    def get_radio_missing_import_dates(cls, radio_name, start_date=None, end_date=None):
        calendar = get_date_range_list(start_date, end_date)

        imports_calendar = cls.query(cls.import_date.distinct()).filter(cls.radio_name == radio_name,
                                                             cls.import_date.between(start_date, end_date)).all()

        imports_calendar = [import_day[0].date() for import_day in imports_calendar]
        missing_days = calendar
        for import_day in imports_calendar:
            if import_day in imports_calendar:
                missing_days.remove(import_day)

        return missing_days