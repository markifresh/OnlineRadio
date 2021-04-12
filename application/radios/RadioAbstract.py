from abc import ABC, abstractmethod
from application.workers.ExtraFunc import get_date_range_list
from concurrent.futures import ThreadPoolExecutor, as_completed


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

    @abstractmethod
    def get_radio_tracks(self, play_date):
        pass

    def get_radio_tracks_per_range(self, start_date=None, end_date=None):
        res = []
        futures = []
        calendar = get_date_range_list(start_date, end_date)

        with ThreadPoolExecutor(max_workers=16) as executor:
            for one_day in calendar:
                futures.append(executor.submit(self.get_radio_tracks, one_day))
        for future in as_completed(futures):
            res.append(future.result())

        return res

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
