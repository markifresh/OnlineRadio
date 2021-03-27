from application.music_services.MSAbstract import MSAbstract
from config import DeezerConfig
from application.pages.oauth_page import deezer_redirect


class Deezer(MSAbstract):
    tracks_search_limit = DeezerConfig.TRACKS_ADD_LIMIT

    def create_token(self):
        deezer_redirect()