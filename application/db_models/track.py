from application.db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime, Boolean, JSON, and_
from application.db_models import radio
from sqlalchemy import or_
from datetime import datetime

class Track(BaseExtended):
    unique_search_field = 'common_name'

    __tablename__ = 'tracks'
    id = Column(Integer, primary_key=True)
    common_name = Column(String(80), Sequence('track_common_name_seq'), unique=True, nullable=False)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album_name = Column(String)
    album_year = Column(String)
    rank = Column(Integer)      # get from deezer / lastfm
    duration = Column(String)   # get from deezer / spotify / lastfm
    play_date = Column(DateTime)
    radio_name = Column(String, ForeignKey('radios.name'), nullable=False)
    # import_date = Column(DateTime, ForeignKey('tracksImports.import_date'))
    # spotify_export_date = Column(Integer, ForeignKey('spotifyExports.export_date'))
    # download_link = Column(String)
    # failed_to_downloaded = Column(String)
    # failed_to_downloaded = Column(Boolean, default=False)
    # reviewed = Column(String)
    # in_spotify = Column(String)
    # failed_to_spotify = Column(String)
    genre = Column(String(20))
    created_on = Column(DateTime(), default=datetime.now)
    services = Column(JSON)
    """
        {"deezer": 2542703, "spotify": "5O4erNlJ74PIF6kGol1ZrC"}
    """


    def __repr__(self):
       return f"<Track(name: {self.common_name} [{self.play_date}], radio: {self.radio_name}, " \
              f"play_date: {self.play_date})>"

    @classmethod
    def query_tracks(cls, start_date='', end_date='', start='', end='', q_filter=''):
        q_selector = cls.query(cls.artist, cls.title).order_by(cls.artist)
        res = cls.query_objects(q_selector=q_selector,
                                q_filter=q_filter,
                                start_date=start_date,
                                end_date=end_date,
                                between_argument='db_import_date')
        res = cls.limit_objects(res, start, end).all()

        return [{'artist': track[0], 'title': track[1]} for track in res]


    @classmethod
    def get_artists(cls, start_id='', limit=''):
        q_selector = cls.query(cls.artist.distinct())
        res = cls.query_objects(q_selector=q_selector).order_by(cls.artist)
        res = cls.limit_objects(res, start_id, limit).all()
        return [artist[0] for artist in res]

        # q_selector = cls.query(cls.artist)
        # res = cls.query_objects(q_selector=q_selector).order_by(cls.artist)
        # res = cls.limit_objects(res, start_id, end_id).all()
        # return res

    @classmethod
    def get_artist_num(cls):
        return {'number': cls.query(cls.artist.distinct()).count()}

    @classmethod
    def get_tracks_per_artist(cls, artist, start_id='', end_id=''):
        q_filter = cls.artist == artist
        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)


    @classmethod
    def get_tracks_per_radio_num(cls, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(q_filter=q_filter, between_argument='db_import_date')


    @classmethod
    def get_tracks_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)


    @classmethod
    def get_tracks_per_radios_num(cls):
        init_dict = {radio.name: 0 for radio in radio.Radio.all()}
        return cls.query_objects_num_all_sorted(between_argument='db_import_date',
                                                sort_argument='radio_name',
                                                init_dict=init_dict)

    @classmethod
    def get_tracks_num(cls):
        return cls.query_objects_num()

    # format start_date='18-09-2020', end_date='19-09-2020'

    @classmethod
    def get_tracks_per_date_per_radios_num(cls, start_date, end_date):
        init_dict = {radio.name: 0 for radio in radio.Radio.all()}
        return cls.query_objects_num_all_sorted(start_date, end_date, between_argument='db_import_date',
                                                sort_argument='radio_name', init_dict=init_dict)


    # @classmethod
    # def get_tracks_per_date_template(cls, start_date, end_date):
    #     return cls.query(cls).filter(cls.db_import_date.between(start_date, end_date))

    @classmethod
    def get_tracks_per_date_num(cls, start_date, end_date):
        return cls.query_objects_num(start_date, end_date, between_argument='db_import_date')



    @classmethod
    def get_tracks_per_date(cls, start_date, end_date, start_id='', end_id=''):
        return cls.query_tracks(start_date=start_date, end_date=end_date, start=start_id, end=end_id)


    @classmethod
    def get_tracks_per_date_per_radio_num(cls, start_date, end_date, radio_name):
        q_filter = cls.radio_name == radio_name
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='db_import_date')

    @classmethod
    def get_tracks_per_date_per_radio(cls, start_date, end_date, radio_name, start_id='', end_id=''):
        q_filter = cls.radio_name == radio_name
        return cls.query_tracks(start_date, end_date, q_filter=q_filter, start=start_id, end=end_id)

### Reviewed tracks per data ###
    @classmethod
    def get_tracks_per_date_reviewed_num_per_radios(cls, start_date, end_date):
        init_dict = {radio.name: 0 for radio in radio.Radio.all()}
        q_filter = cls.reviewed == True
        return cls.query_objects_num_all_sorted(start_date, end_date, between_argument='db_import_date',
                                                sort_argument='radio_name', init_dict=init_dict, q_filter=q_filter)

    @classmethod
    def get_tracks_reviewed_num_per_radios(cls):
        init_dict = {radio.name: 0 for radio in radio.Radio.all()}
        q_filter = cls.reviewed == True
        return cls.query_objects_num_all_sorted(sort_argument='radio_name', init_dict=init_dict, q_filter=q_filter)


    @classmethod
    def get_tracks_per_date_reviewed(cls, start_date, end_date, start_id='', end_id=''):
        q_filter = cls.reviewed == True
        return cls.query_tracks(start_date=start_date, end_date=end_date, start=start_id, end=end_id, q_filter=q_filter)


    @classmethod
    def get_tracks_per_date_reviewed_num(cls, start_date, end_date):
        q_filter = cls.reviewed == True
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='db_import_date')


    @classmethod
    def get_tracks_per_date_reviewed_per_radio(cls, start_date, end_date, radio_name, start_id='', end_id=''):
        q_filter = (cls.reviewed == True) & (cls.radio_name == radio_name)
        return cls.query_tracks(start_date=start_date, end_date=end_date,  start=start_id, end=end_id, q_filter=q_filter)


    @classmethod
    def get_tracks_per_date_reviewed_num_per_radio(cls, start_date, end_date, radio_name):
        q_filter = (cls.reviewed == True) & (cls.radio_name == radio_name)
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='db_import_date')


### NOT Reviewed tracks per data ###
    @classmethod
    def get_tracks_per_date_reviewed_not_num_per_radios(cls, start_date, end_date):
        init_dict = {radio.name: 0 for radio in radio.Radio.all()}
        q_filter = (cls.reviewed == None) | (cls.reviewed == False)
        return cls.query_objects_num_all_sorted(start_date, end_date, between_argument='db_import_date',
                                                 sort_argument='radio_name', init_dict=init_dict, q_filter=q_filter)

    @classmethod
    def get_tracks_reviewed_not_num_per_radios(cls):
        init_dict = {radio.name: 0 for radio in radio.Radio.all()}
        q_filter = (cls.reviewed == None) | (cls.reviewed == False)
        return cls.query_objects_num_all_sorted(sort_argument='radio_name', init_dict=init_dict, q_filter=q_filter)

    @classmethod
    def get_tracks_per_date_reviewed_not(cls, start_date, end_date, start_id='', end_id=''):
        q_filter = (cls.reviewed == None) | (cls.reviewed == False)
        return cls.query_tracks(start_date=start_date, end_date=end_date, start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_tracks_per_date_reviewed_not_num(cls, start_date, end_date):
        q_filter = (cls.reviewed == None) | (cls.reviewed == False)
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='db_import_date')


    @classmethod
    def get_tracks_per_date_reviewed_not_per_radio(cls, start_date, end_date, radio_name, start_id='', end_id=''):
        q_filter = ((cls.reviewed == None) | (cls.reviewed == False)) & (cls.radio_name == radio_name)
        return cls.query_tracks(start_date=start_date, end_date=end_date, start=start_id, end=end_id, q_filter=q_filter)


    @classmethod
    def get_tracks_per_date_reviewed_not_num_per_radio(cls, start_date, end_date, radio_name):
        q_filter = ((cls.reviewed == None) | (cls.reviewed == False)) & (cls.radio_name == radio_name)
        return cls.query_objects_num(start_date, end_date, q_filter=q_filter, between_argument='db_import_date')



    def export_tracks_to_spotify(self):
        pass

    def get_download_links_for_tracks(self):
        pass

    def get_youtube_links_for_tracks(self):
        pass

    # @classmethod
    # def get_tracks_query(cls, start='', end=''):
    #     if not start:
    #         start = 0
    #
    #     if not end:
    #         end = 50
    #
    #     # return cls.query(cls.artist, cls.title).offset(start).limit(end).all()
    #     if q_filter:
    #         res = cls.query(cls.artist, cls.title).filter(q_filter).offset(start).limit(end).all()
    #     else:
    #         res = cls.query(cls.artist, cls.title).offset(start).limit(end).all()
    #     return [{'artist': track[0], 'title': track[1]} for track in res]

    # @classmethod
    # def get_tracks_all(cls, start='', end='', q_filter=''):
    #     q_selector = cls.artist, cls.title
    #     res = cls.query_objects(q_selector=q_selector, q_filter=q_filter)
    #     res = cls.limit_objects(res, start, end).all()
    #
    #     return [{'artist': track[0], 'title': track[1]} for track in res]

    @classmethod
    def get_tracks(cls, start_id='', end_id=''):
        return cls.query_tracks(start=start_id, end=end_id)

    @classmethod
    def get_track(cls, common_name):
        return cls.query(cls).filter(cls.common_name == common_name).one_or_none()

#### NOT Reviewed Tracks ####
    @classmethod
    def get_tracks_reviewed_not(cls, start_id='', end_id=''):
        q_filter = (cls.reviewed == None) | (cls.reviewed == False)
        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_tracks_reviewed_not_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = ((cls.reviewed == None) | (cls.reviewed == False)) & (cls.radio_name == radio_name)
        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)


    @classmethod
    def get_tracks_reviewed_not_num(cls):
        q_filter = (cls.reviewed == None) | (cls.reviewed == False)
        return cls.query_objects_num(q_filter=q_filter)


    @classmethod
    def get_tracks_reviewed_not_per_radio_num(cls, radio_name):
        q_filter = ((cls.reviewed == None) | (cls.reviewed == False)) & (cls.radio_name == radio_name)
        return cls.query_objects_num(q_filter=q_filter)

    @classmethod
    def get_tracks_exported_not_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = (cls.radio_name == radio_name) & \
                   ((cls.in_spotify == None) | (cls.in_spotify == False)) & \
                   ((cls.failed_to_spotify == None) | (cls.failed_to_spotify == False))


        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_tracks_exported_not_per_radio_num(cls, radio_name):
        q_filter = (cls.radio_name == radio_name) & \
                   ((cls.in_spotify == None) | (cls.in_spotify == False)) & \
                   ((cls.failed_to_spotify == None) | (cls.failed_to_spotify == False))

        return cls.query_objects_num(q_filter=q_filter)

    @classmethod
    def get_tracks_exported_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = (cls.radio_name == radio_name) & \
                   (((cls.in_spotify != None) & (cls.in_spotify != False))  |
                   ((cls.failed_to_spotify != None) & (cls.failed_to_spotify != False)))

        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)


    @classmethod
    def get_tracks_exported_failed_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = (cls.radio_name == radio_name) & \
                   ((cls.failed_to_spotify != None) & (cls.failed_to_spotify != False))

        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)

#### Reviewed Tracks ####
    @classmethod
    def get_tracks_reviewed(cls, start_id='', end_id=''):
        q_filter = (cls.reviewed == True)
        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_tracks_reviewed_per_radio(cls, radio_name, start_id='', end_id=''):
        q_filter = (cls.reviewed == True) & (cls.radio_name == radio_name)
        return cls.query_tracks(start=start_id, end=end_id, q_filter=q_filter)

    @classmethod
    def get_tracks_reviewed_num(cls):
        q_filter = (cls.reviewed == True)
        return cls.query_objects_num(q_filter=q_filter)


    @classmethod
    def get_tracks_reviewed_per_radio_num(cls, radio_name):
        q_filter = (cls.reviewed == True) & (cls.radio_name == radio_name)
        return cls.query_objects_num(q_filter=q_filter)
