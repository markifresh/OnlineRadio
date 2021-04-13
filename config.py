from dotenv import load_dotenv
from pathlib import Path
from os import getenv
from logging import INFO, DEBUG

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

user_settings = [
                   {'option_name': 'daily_subscription',
                   'description': 'Each day you will receive all tracks for previous day per radios'},

                   {'option_name': 'daily_export',
                   'description': 'Each day all added tracks will be exported to your Music Service'},

                   {'option_name': 'auto_export',
                   'description': 'Automatically add all tracks to your Music Service'},

                   {'option_name': 'auto_liked',
                   'description': 'Automatically add liked tracks to your Music Service'},
                ]

def config_class_to_dict(confClass):
     class_keys = [key for key in vars(confClass).keys() if '__' not in key]
     return {key: getattr(confClass, key) for key in class_keys}


class Config:
    """Base config."""
    SECRET_KEY = getenv('SECRET_KEY')
    SESSION_COOKIE_NAME = getenv('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESTX_MASK_SWAGGER = False
    # RESTX_VALIDATE = True


class CaptchaConfig:
    RECAPTCHA_PUBLIC_KEY = getenv('google_captcha_public')
    RECAPTCHA_PRIVATE_KEY = getenv('google_captcha_private')
    RECAPTCHA_OPTIONS = {'theme': 'white'}
    RECAPTCHA_USE_SSL = False


class ProdConfig(Config, CaptchaConfig):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = f'sqlite:///{getenv("PROD_DATABASE_URI")}'
    DATABASE_ECHO = False
    DATABASE_LOG_LEVEL = INFO
    DATABASE_LOG_FILE = 'prod_db_logs.log'
    PORT = 8080
    # SERVER_NAME = 'prodradio.localdomain'
    HOST = '0.0.0.0'


class DevConfig(Config, CaptchaConfig):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    DATABASE_URI = f'sqlite:///{getenv("DEV_DATABASE_URI")}'
    DATABASE_ECHO = False
    DATABASE_LOG_LEVEL = INFO
    DATABASE_LOG_FILE = 'dev_db_logs.log'
    PORT = 5000
    # SERVER_NAME = 'devradio.localdomain'
    HOST = '127.0.0.1'



class APIConfig:
    radiofrance_api_key = getenv('RADIOFRANCE_API_KEY')
    spotify_api_id = getenv('SPOTIFY_API_ID')
    spotify_api_key = getenv('SPOTIFY_API_KEY')
    youtube_api_key = getenv('YOUTUBE_API_KEY')
    api_envelope = 'result'


class RadioConfig:
    exclude_radios = ['FIP_REGGAE', 'FIP_METAL']
    url_api_open_radio = 'https://openapi.radiofrance.fr/v1/graphql'

    djam_radio = {'id': 'DJAM',
                  'url': 'https://www.djamradio.com',
                  'stream_url': 'https://ledjamradio.ice.infomaniak.ch/ledjamradio.mp3',
                  'tracks_request_url': 'https://www.djamradio.com/actions/retrieve.php',
                  'current_playing_url': 'https://www.djamradio.com/actions/infos.php'}

    fip_radio = {'id': 'FIP',
                 'url': 'https://www.fip.fr/',
                 'tracks_request_url': url_api_open_radio}


class MusicService:
    DEFAULT_PLAYLIST_DESCRIPTION = 'playlist for radio_app'
    DEFAULT_PLAYLIST_NAME = 'Radio_'    # + Radio Name


class SpotifyConfig(MusicService):
    SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    SPOTIFY_API_BASE_URL = "https://api.spotify.com"
    SPOTIFY_USER_ACC_LINK = "https://open.spotify.com/user"
    SPOTIFY_API_VERSION = "v1"
    SPOTIFY_API_URL = f"{SPOTIFY_API_BASE_URL}/{SPOTIFY_API_VERSION}/"
    SCOPE = "playlist-modify-public playlist-modify-private playlist-read-private"
    CLIENT_ID = APIConfig.spotify_api_id
    CLIENT_KEY = APIConfig.spotify_api_key
    PLAYLISTS_REQUEST_LIMIT = 50
    PLAYLIST_TRACKS_REQUEST_LIMIT = 100
    TRACKS_SEARCH_LIMIT = 100
    TRACKS_ADD_LIMIT = 100

class DeezerConfig(MusicService):
    DEEZER_URL = "https://www.deezer.com"
    DEEZER_AUTH_URL = "https://connect.deezer.com/oauth/auth.php"
    DEEZER_TOKEN_URL = "https://connect.deezer.com/oauth/access_token.php"
    DEEZER_API_BASE_URL = "https://api.deezer.com"
    # DEEZER_API_VERSION = "v1"
    # DEEZER_API_URL = f"{DEEZER_API_BASE_URL}/{DEEZER_API_VERSION}"
    SCOPE = "basic_access,manage_library,delete_library"
    CLIENT_ID = getenv('DEEZER_CLIENT_ID')
    CLIENT_SECRET = getenv('DEEZER_CLIENT_SECRET')
    PLAYLISTS_REQUEST_LIMIT = 50
    PLAYLIST_TRACKS_REQUEST_LIMIT = 100
    TRACKS_SEARCH_LIMIT = 50
    TRACKS_ADD_LIMIT = 100


class DBConfig:
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s'


