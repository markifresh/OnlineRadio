from config import DevConfig
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging


db_logs_handler = logging.FileHandler('sqlite.log')
db_logs_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
db_logs_handler.setFormatter(formatter)

db_logger = logging.getLogger('sqlalchemy.engine')
db_logger.addHandler(db_logs_handler)
db_logger.setLevel(logging.INFO)


Base = declarative_base()
engine = create_engine(DevConfig.DATABASE_URI, echo=DevConfig.DATABASE_ECHO)
db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from .dbimport_db import DBImport
from .radio_db import Radio
from .track_db import Track
from .spotifyexport_db import SpotifyExport

for db_model in (DBImport, Radio, Track, SpotifyExport):
    db_model.set_session()

# def local_db_init():
#     DBImport_model = DBImport(db_session())
#     Track_model = Track(db_session())
#     Radio_model = Radio(db_session())
#     SpotifyExport_model = SpotifyExport(db_session())
#
# def app_db_init(app_session):
#     DBImport_model = DBImport(app_session)
#     Track_model = Track(app_session)
#     Radio_model = Radio(app_session)
#     SpotifyExport_model = SpotifyExport(app_session)
#
# local_db_init()