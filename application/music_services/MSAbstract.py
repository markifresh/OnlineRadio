from abc import ABC, abstractmethod
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


class MSAbstract(ABC):
    token = ''
    token_expiration_time = datetime(year=1970, month=1, day=1)
    tracks_search_limit = 10

    def token_expired(self):
        return self.token_expiration_time < datetime.now()

    @abstractmethod
    def create_token(self):
        pass

    def set_token(self, token, token_expiration_time):
        self.token = token
        self.token_expiration_time = token_expiration_time

    @abstractmethod
    def get_user_info(self):
        pass

    @abstractmethod
    def create_playlist(self, name):
        pass

    @abstractmethod
    def sort_playlist(self):
        pass

    @abstractmethod
    def get_user_playlists(self):
        pass

    @abstractmethod
    def get_user_radios_playlists(self):
        pass

    @abstractmethod
    def get_playlist_tracks(self):
        pass

    @abstractmethod
    def add_track_to_playlist(self):
        pass

    @abstractmethod
    def add_tracks_to_playlist(self):
        pass

    @abstractmethod
    def remove_track_from_playlist(self):
        pass

    @abstractmethod
    def find_track(self):
        pass

    def find_tracks(self):
        pass



