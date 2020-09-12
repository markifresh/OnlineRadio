import config
from sqlalchemy import Column, Integer, String, ForeignKey, Sequence
from sqlalchemy.orm import relationship, query
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from Worker import DBWorker
from time import sleep
from sqlalchemy.orm import sessionmaker
from traceback import format_exc as traceback_format_exc


Base = declarative_base()

class BaseExtended(Base):
    __abstract__ = True

    Base.dbw = DBWorker()
    Base.metadata.bind = create_engine(f'sqlite:///{config.db_location}', echo=True)

    @classmethod
    def create_db_session(cls):
        Session = sessionmaker(bind=Base.metadata.bind)
        session = Session()
        return session


    @classmethod
    def get_all_objects(cls):
        db_session = cls.create_db_session()
        res = db_session.query(cls).all()
        db_session.close()
        return res

    @classmethod
    def to_json(cls, db_objects):
        if isinstance(db_objects, query.Query):
            db_objects = db_objects.all()

        elif isinstance(db_objects, cls):
            db_objects = [db_objects]

        if not isinstance(db_objects, list) or len(db_objects) == 0:
            return {}


        res = {}
        col_names = db_objects[0].__table__.columns.keys()
        prime_key = cls.__table__.primary_key.columns.values()[0].name

        for db_object in db_objects:
            obj = {}
            for col_name in col_names:
                obj[col_name] = getattr(db_object, col_name)
            res[getattr(db_object, prime_key)] = obj

        return res

class Track(BaseExtended):
    __tablename__ = 'tracks'

    common_name = Column(String(80), Sequence('track_common_name_seq'), unique=True, nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album_name = Column(String)
    album_year = Column(String)
    duration = Column(String)
    play_date = Column(String(30))
    radio_id = Column(String, ForeignKey('radios.id'), nullable=False)
    db_import_id = Column(String, ForeignKey('dbImports.id'))
    spotify_export_id = Column(Integer, ForeignKey('spotifyExports.id'))
    download_link = Column(String)
    failed_to_downloaded = Column(String)
    reviewed = Column(String)
    in_spotify = Column(String)
    failed_to_spotify = Column(String)
    genre = Column(String(20))
    youtube_link = Column(String)

    def __repr__(self):
       return f"<Track(name: {self.common_name}, radio: {self.radio_id}, import time: {self.db_import_id})>"

    def get_artists(self):
        pass

class Radio(BaseExtended):
    __tablename__ = 'radios'
    id = Column(String(20), Sequence('radio_id_seq'), primary_key=True, unique=True)    # id from api
    url = Column(String(80))
    db_imports = relationship('DBImport', lazy=True)
    spotify_exports = relationship('SpotifyExport', lazy=True)
    tracks = relationship('Track', lazy=True)

    def __repr__(self):
       return f"<Radio({self.id})>"

    @classmethod
    def update_radios_list(cls):
        return cls.dbw.update_radios_list_db(cls)

    @classmethod
    def update_radios_tracks(cls):
        results = {}
        radios = cls.get_all_objects()
        for radio in radios:

            try:
                res = radio.import_tracks_to_db()
                results[radio.id] = res

            except:
                results[radio.id] = {'success': False, 'result': traceback_format_exc()}

        return results

    def import_tracks_to_db(self):
        return self.dbw.update_radio_tracks(self, Track, DBImport)
    
    def export_tracks_to_spotify(self):
        pass
        
    def get_download_links_for_tracks(self):
        pass
    
    def get_youtube_links_for_tracks(self):
        pass

    def get_tracks_number(self):
        db_session = self.create_db_session()
        num = db_session.query(Track).filter(Track.radio_id == self.id).count()
        db_session.close()
        return num

    def get_latest_import(self):
        db_session = self.create_db_session()
        db_import = db_session.query(DBImport).filter(DBImport.radio_id == self.id).all()[-1]
        db_session.close()
        return db_import.id.split('.')[0] if db_import else 'no imports'

    @classmethod
    def get_all_radios_json(cls):
        radios = cls.get_all_objects()
        js_objects = cls.to_json(radios)
        for radio in radios:
            js_objects[radio.id]['num_tracks'] = radio.get_tracks_number()
            js_objects[radio.id]['latest_dbimport'] = radio.get_latest_import()
        return js_objects

class DBImport(BaseExtended):
    __tablename__ = 'dbImports'

    id = Column(String(50), Sequence('dbimport_id_seq'), primary_key=True, unique=True)  # update time in ms
    tracks = relationship('Track', lazy=True)
    num_tracks_added = Column(Integer)
    num_tracks_requested = Column(Integer)
    radio_id = Column(String(20), ForeignKey('radios.id'), nullable=False)
   
    def __repr__(self):
       return f"<dbImport({self.id}, {self.radio_id}, {self.num_tracks_added} vs {self.num_tracks_requested})>"

       
class SpotifyExport(BaseExtended):
    __tablename__ = 'spotifyExports'

    id = Column(Integer, Sequence('spotifyexports_id_seq'),  primary_key=True, unique=True) # update_time in ms
    tracks = relationship('Track', lazy=True)
    radio_id = Column(String(20), ForeignKey('radios.id'), nullable=False)
    num_tracks_added = Column(Integer)
    num_tracks_requested = Column(Integer)
    num_tracks_reviewed = Column(Integer)
    # tracks_reviewed = tracs_ref
   
    def __repr__(self):
       return f"<spotifyExport({self.id}, {self.radio_id}, {self.num_tracks_requested} vs {self.num_tracks_added})>"

def create_tables():
    engine = create_engine(f'sqlite:///{config.db_location}', echo=True)
    Base.metadata.create_all(engine)







# engine = create_engine('sqlite:///:memory:', echo=True)



# from sqlalchemy.orm import sessionmaker
# Session = sessionmaker(bind=engine)
# session = Session()
# ed_user = User(name='ed', fullname='Ed Jones', nickname='edsnickname')
# session.add(ed_user)
#
#
# our_user = session.query(User).filter_by(name='ed').first()
# ed_user is our_user
# True
#
# session.add_all([
# ...     User(name='wendy', fullname='Wendy Williams', nickname='windy'),
# ...     User(name='mary', fullname='Mary Contrary', nickname='mary'),
# ...     User(name='fred', fullname='Fred Flintstone', nickname='freddy')])
#
# session.new
# IdentitySet([<User(name='wendy', fullname='Wendy Williams', nickname='windy')>,
# <User(name='mary', fullname='Mary Contrary', nickname='mary')>,
# <User(name='fred', fullname='Fred Flintstone', nickname='freddy')>])
#
# session.commit()


# with engine.connect() as connection:
#     result = connection.execute("select username from users")
#     for row in result:
#         print("username:", row['username'])