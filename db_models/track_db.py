from db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, and_


class Track(BaseExtended):
    unique_search_field = 'common_name'

    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    common_name = Column(String(80), Sequence('track_common_name_seq'), unique=True, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album_name = Column(String)
    album_year = Column(String)
    duration = Column(String)
    play_date = Column(String(30))
    radio_name = Column(String, ForeignKey('radios.name'), nullable=False)
    db_import_date = Column(String, ForeignKey('dbImports.import_date'))
    spotify_export_date = Column(Integer, ForeignKey('spotifyExports.export_date'))
    download_link = Column(String)
    failed_to_downloaded = Column(String)
    reviewed = Column(String)
    in_spotify = Column(String)
    failed_to_spotify = Column(String)
    genre = Column(String(20))
    youtube_link = Column(String)

    def __repr__(self):
       return f"<Track(name: {self.common_name}, radio: {self.radio_name}, import time: {self.db_import_date})>"

    @classmethod
    def get_artists(cls):
        db_session = cls.create_db_session()
        res = [artist[0] for artist in db_session.query(cls.artist).all()]
        return sorted(set(res))

    @classmethod
    def get_num_tracks_per_radio(cls, radio_name):
        db_session = cls.create_db_session()
        res = (db_session.query(cls).filter(cls.radio_name == radio_name)).count()
        db_session.close()
        return res

    @classmethod
    def get_tracks_per_radio(cls, radio_name):
        db_session = cls.create_db_session()
        res = (db_session.query(cls).filter(cls.radio_name == radio_name)).all()
        db_session.close()
        return cls.to_json(res)

    @classmethod
    def get_num_tracks_per_radios(cls):
        db_session = cls.create_db_session()

        radios = [radio[0] for radio in db_session.query(cls.radio_name).all()]
        res = {}
        for radio in radios:
            res[radio] = res[radio] + 1 if radio in res.keys() else 1

        db_session.close()
        return res

    # format start_date='18-09-2020', end_date='19-09-2020'
    @classmethod
    def get_num_tracks_per_radio_per_date(cls, radio='', start_date='', end_date=''):
        res = {}
        if start_date and end_date:

            if isinstance(start_date, str) == isinstance(end_date, str) == True:
                if '-' in start_date and '-' in end_date:
                    start_day = int(start_date.split('-')[0])
                    end_day = int(end_date.split('-')[0])
                    print(start_day, end_day)
                    if end_day - start_day < 1:
                        return {'result': 'difference in days less than 1'}

                    start_date = start_date.replace('-', '/')
                    end_date = end_date.replace('-', '/')
                    db_session = cls.create_db_session()
                    if radio:
                        res = db_session.query(cls).filter(and_(
                                cls.radio_name == radio,
                                cls.db_import_date.between(start_date, end_date))).count()

                    else:
                        radios = db_session.query(cls.radio_name).\
                            filter(cls.db_import_date.between(start_date, end_date)).all()
                        radios = [radio[0] for radio in radios]
                        res = {}
                        for radio in radios:
                            res[radio] = res[radio] + 1 if radio in res.keys() else 1

                    db_session.close()

            # elif isinstance(play, datetime):
            #     orig_date = play_date.strftime('%d/%m/%Y')
            #     day = play_date.day
            #     play_date = datetime(year=play_date.year, month=play_date.month, day=play_date.day)

        return res

    def export_tracks_to_spotify(self):
        pass

    def get_download_links_for_tracks(self):
        pass

    def get_youtube_links_for_tracks(self):
        pass