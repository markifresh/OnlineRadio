def create_db(config_class):
    from config import DBConfig
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import logging

    db_logs_handler = logging.FileHandler(config_class.DATABASE_LOG_FILE)
    db_logs_handler.setLevel(config_class.DATABASE_LOG_LEVEL)
    formatter = logging.Formatter(DBConfig.LOG_FORMAT)
    db_logs_handler.setFormatter(formatter)

    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.addHandler(db_logs_handler)
    db_logger.setLevel(config_class.DATABASE_LOG_LEVEL)


    engine = create_engine(config_class.DATABASE_URI, echo=config_class.DATABASE_ECHO)
    db_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return db_session

def init_db_locally(config_class):
    pass
# from .dbimport_db import DBImport
# from .radio_db import Radio
# from .track_db import Track
# from .spotifyexport_db import SpotifyExport
#
# for db_model in (DBImport, Radio, Track, SpotifyExport):
#     db_model.set_session()

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