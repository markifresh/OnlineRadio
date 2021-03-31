from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor


class MSAbstract(ABC):
    api_url = ''
    token_expiration_time = datetime(year=1970, month=1, day=1)
    tracks_search_limit = 10

    # def __init__(self, token='', expires_in_sec=0):
    #     self.token_expiration_time = datetime.now() + timedelta(seconds=int(expires_in_sec))
    #     self.token = token
# class MSService(MSAbstract):
#     @abstractmethod
#     def get_requests(self):
#         pass
#
#     @abstractmethod
#     def post_requests(self):
#         pass
#
#     @abstractmethod
#     def delete_requests(self):
#         pass

    # @abstractmethod
    # def find_track(self, common_name):
    #     pass

    def find_tracks(self, tracks_list):
        pass


# # class MSUser(MSService):
    def token_expired(self):
        return self.token and self.token_expiration_time < datetime.now()

    # @abstractmethod
    # def create_token(self):
    #     pass

    def set_token(self, token, expires_in_sec):
        self.token = token
        self.token_expiration_time = datetime.now() + timedelta(seconds=int(expires_in_sec))

    @abstractmethod
    def get_user_info(self):
        pass

    @abstractmethod
    def create_playlist(self, name):
        pass

    # @abstractmethod
    # def sort_playlist(self):
    #     pass

    @abstractmethod
    def get_user_playlists(self):
        pass

    @abstractmethod
    def get_user_radios_playlists(self):
        pass

    @abstractmethod
    def get_user_playlist_by_name(self, playlist_name):
        pass

    @abstractmethod
    def get_playlist_tracks(self, playlist_id):
        pass

    #todo: check if track already in playlists
    @abstractmethod
    def add_track_to_playlist(self, playlist_id, track_id):
        pass

    #todo: check if tracks already in playlists
    @abstractmethod
    def add_tracks_to_playlist(self, playlist_id, tracks_ids):
        pass

    # @abstractmethod
    # def remove_track_from_playlist(self, playlist_id, track_id):
    #     pass




