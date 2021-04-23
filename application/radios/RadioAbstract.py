from abc import ABC, abstractmethod
from application.workers.ExtraFunc import get_date_range_list
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import import_datetime_format, import_date_format
from datetime import datetime, timedelta, date
from application import convert_to_date


class RadioAbstract(ABC):
    radio_id = ''
    url = ''
    tracks_request_url = ''
    stream_url = ''
    current_playing_url = ''
    genre = 'not set'
    description = 'default radio description'
    country = 'Country not set'

    @abstractmethod
    def __init__(self, radio_id):
        self.radio_id = radio_id

    def get_radio_tracks(self, play_date):
        play_date = convert_to_date(play_date)
        day_before = play_date + timedelta(days=1)
        return self.get_radio_tracks_per_range(day_before, play_date)

    @abstractmethod
    def get_radio_tracks_per_range(self, start_date, end_date):
        pass

    @abstractmethod
    def get_current_track(self):
        pass

    @abstractmethod
    def get_latest_tracks(self):
        pass

    @classmethod
    def get_radios(cls):
        return {'success': True, 'result': {cls.radio_id: {
                                                            'name': cls.radio_id,
                                                            'url': cls.url,
                                                            'stream_url': cls.stream_url,
                                                            'genre': cls.genre,
                                                            'description': cls.description,
                                                            'country': cls.country}}}
