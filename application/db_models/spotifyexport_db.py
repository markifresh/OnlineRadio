from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from application.db_models import track_db
from datetime import datetime


class SpotifyExport(BaseExtended):
    unique_search_field = 'export_date'

    __tablename__ = 'spotifyExports'
    id = Column(Integer, primary_key=True)
    export_date = Column(DateTime, Sequence('spotifyexports_export_date_seq'), unique=True)  # update_time in ms
    tracks = relationship('track_db.Track', lazy='dynamic')
    radio_name = Column(String(20), ForeignKey('radios.name'), nullable=False)
    num_tracks_added = Column(Integer, default=0)
    num_tracks_requested = Column(Integer, default=0)
    num_tracks_reviewed = Column(Integer, default=0)

    # tracks_reviewed = tracs_ref

    def __repr__(self):
        return f"<spotifyExport({self.export_date}, {self.radio_name}, " \
               f"{self.num_tracks_requested} vs {self.num_tracks_added})>"


    @classmethod
    def query_exports(cls, start_date='', end_date='', start='', end='', q_filter=''):
        q_selector = cls.query(cls.export_date, cls.radio_name, cls.num_tracks_added)
        res = cls.query_objects(q_selector=q_selector,
                                q_filter=q_filter,
                                start_date=start_date,
                                end_date=end_date,
                                between_argument='export_date')
        res = cls.limit_objects(res, start, end).all()

        return [{'export_date': export[0], 'radio_name': export[1], 'num_tracks_added': export[2]} for export in res]

    @classmethod
    def get_exports_per_date(cls, start_date, end_date, start_id='', end_id=''):
        return cls.query_exports(start_date=start_date, end_date=end_date, start=start_id, end=end_id)

    @classmethod
    def get_exports_per_date_num(cls, start_date, end_date):
        return cls.query_objects_num(start_date, end_date, between_argument='export_date')


    @classmethod
    def get_exports_num(cls):
        return cls.query_objects_num()

    @classmethod
    def get_export_by_date(cls, export_date):
        if isinstance(export_date, str):
            export_date = datetime.strptime(export_date, '%Y-%m-%dT%H:%M:%S.%f')

        q_filter = cls.export_date == export_date
        return cls.query_objects(q_filter=q_filter).one_or_none()

    @classmethod
    def get_exports_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_exports(start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_exports_per_radios(cls):
        exports = cls.session.query(cls).all()
        res = {}
        for export in exports:
            if export.radio_name in res.keys():
                res[export.radio_name].append(export)
            else:
                res[export.radio_name] = [export]
        cls.session.close()
        return res

    @classmethod
    def get_exports_num_per_radio(cls, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(q_filter=q_filter, between_argument='export_date')

    @classmethod
    def get_exports_num_per_radios(cls):

        radios = [radio[0] for radio in cls.session.query(cls.radio_name).all()]
        res = {}
        for radio in radios:
            res[radio] = res[radio] + 1 if radio in res.keys() else 1

        cls.session.close()
        return res

    @classmethod
    def get_latest_export_for_radio(cls, radio_name):
        return cls.query(cls).filter(cls.radio_name == radio_name).order_by(cls.export_date.desc()).first()

    @classmethod
    def get_exports_per_date_per_radio(cls, start_date, end_date, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_exports(start_date, end_date, q_filter=q_filter, start=start_id, end=end_id)

    @classmethod
    def get_exports_per_date_per_radio_num(cls, start_date, end_date, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='export_date')

    @classmethod
    def export_radio(cls, radio_name):
        pass