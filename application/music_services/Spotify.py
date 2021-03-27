from application.music_services import MSAbstract
from config import SpotifyConfig


class Spotify(MSAbstract):
    tracks_search_limit = SpotifyConfig.TRACKS_SEARCH_LIMIT
