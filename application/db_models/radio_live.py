from sqlalchemy import Column, Integer, Boolean, DateTime, String
from datetime import datetime

from application.db_models.extenders_for_db_models import BaseExtended
from application.schema_models.validators import validate_radio_name
from application.workers.RadioWorker import create_radio
from application.workers.ServiceWorker import find_track
from application.db_models import track
from application.CustomExceptions import BasicCustomException

class  Radio(BaseExtended):

    __tablename__ = 'radio_lives'
    id = Column(Integer, primary_key=True)
    radio_name = Column(String)
    valid_till = Column(DateTime)
    updating = Column(Boolean)
    update_completed = Column(Boolean)
    tracK_found = Column(Boolean)
    track_id = Column(Integer)
    common_name = Column(String)

    def __repr__(self):
        return f"Radio {self.radio_name} - {self.common_name}"


    @classmethod
    def get_live(cls, radio_name):
        validate_radio_name(radio_name)
        latest_live = cls.query(cls).filter(cls.radio_name == radio_name).orderby(cls.id.desc()).first()
        track_db = track.Track

        if latest_live and latest_live.valid_till > datetime.now():
            latest_live.track = track_db.get_track(latest_live.track_id)
            return latest_live

        elif latest_live.updationg:
            return 'Come later, updating...'

        else:
            latest_live_id = cls.commit_data({'updating': True})['id']

            radio_obj = create_radio(radio_name)
            live_track = radio_obj.get_current_track()

            if not track_db.get_track(live_track['common_name']):
                music_services = find_track(live_track)
                track_dict = {
                                'common_name': live_track['common_name'],
                                'title': live_track['title'],
                                'artist': live_track['artist'],
                                'radio_name': radio_name,
                                'rank': music_services['rank'],
                                'services': music_services['services']
                            }
                res = track_db.commit_data(track_dict)
                if not res['success']:
                    raise BasicCustomException(f'Failed to add track to DB: {str(res)}')

                track_dict['id'] = res['id']

            latest_live_data = {'id': latest_live_id, 'updating': False}
            cls.update_row(latest_live_data)
            return ...

