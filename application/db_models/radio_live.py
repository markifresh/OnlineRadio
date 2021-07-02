from sqlalchemy import Column, Integer, Boolean, DateTime, String
from datetime import datetime, timedelta

from application.db_models.extenders_for_db_models import BaseExtended
from application.schema_models import validators
from application.workers.RadioWorker import create_radio
from application.workers.ServiceWorker import find_track
from application.db_models import track
from application.CustomExceptions import BasicCustomException


class RadioLive(BaseExtended):
    unique_search_field = 'radio_name'

    __tablename__ = 'radio_lives'
    id = Column(Integer, primary_key=True)
    radio_name = Column(String, unique=True)
    valid_till = Column(DateTime, default=datetime.now())
    updating = Column(Boolean)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    update_duration = Column(Integer)
    track_id = Column(Integer)
    track_duration = Column(Integer)
    common_name = Column(String)

    def __repr__(self):
        return f"Radio {self.radio_name} - {self.common_name}"


    @classmethod
    def get_live(cls, radio_name):
        validators.validate_radio_name(radio_name)
        latest_live = cls.query(cls).filter(cls.radio_name == radio_name).order_by(cls.id.desc()).first()
        now = datetime.now()

        # If updating and time of update > 15 seconds - FAIL
        if latest_live and latest_live.updating:
            cls.session.close()
            success = (now - latest_live.start_date).seconds < 15
            if success:
                latest_live.need_to_wait = True
            return {'success': success, 'updated': False, 'result': latest_live}

        elif latest_live and latest_live.valid_till > now and (latest_live.valid_till - now).seconds > 0:
            track_db = track.Track()
            if latest_live.track_id != 0:
                latest_live.track = track_db.get_track(latest_live.track_id)
            else:
                latest_live.track = {'artist': 'unknown', 'title': 'unknown', 'id': 0}

            latest_live.check_within = (latest_live.valid_till - now).seconds
            latest_live.need_to_wait = False
            track_db.session.close()
            cls.session.close()
            return {'success': True, 'updated': False, 'result': latest_live}

        else:
            start_date = datetime.now()
            new_data = {'radio_name': radio_name, 'updating': True, 'start_date': start_date}
            res = cls.update_row(new_data, create_new=True)
            if not res['success']:
                raise BasicCustomException(f'Failed to add track to DB: {str(res)}')

            radio_obj = create_radio(radio_name)
            live_track = radio_obj.get_current_track()
            track_duration = (live_track['end_date'] - live_track['start_date']).seconds
            track_db = track.Track()
            track_new = track_db.get_track(live_track['common_name'])
            track_db.session.close()
            if not track_new:
                if live_track['common_name'] != 'unknown - unknown':
                    music_services = find_track(live_track)
                    track_new = {
                                    'common_name':  live_track['common_name'],
                                    'title':        live_track['title'],
                                    'artist':       live_track['artist'],
                                    'radio_name':   radio_name,
                                    'rank':         music_services['rank'],
                                    'services':     music_services['services'],
                                    'play_date':    live_track['start_date']
                                 }
                    res = track_db.commit_data(track_new)
                    if not res['success']:
                        raise BasicCustomException(f'Failed to add track to DB: {str(res)}')
                    track_db = track.Track()
                    track_new = track_db.get_track(live_track['common_name'])
                    track_db.session.close()
                else:
                    track_new = live_track
                    track_new['id'] = 0

            track_id = track_new.id if not isinstance(track_new, dict) else track_new['id']
            track_common_name = track_new.common_name if not isinstance(track_new, dict) else track_new['common_name']
            end_date = datetime.now()
            latest_live_data = {
                                    'radio_name':       radio_name,
                                    'valid_till':       live_track['end_date'],
                                    'updating':         False,
                                    'end_date':         end_date,
                                    'update_duration':  (end_date - start_date).seconds,
                                    'track_id':         track_id,
                                    'track_duration':   track_duration,
                                    'common_name':      track_common_name,
                                }
            res = cls.update_row(latest_live_data)
            if not res['success']:
                raise BasicCustomException(f'Failed to add track to DB: {str(res)}')

            latest_live = cls.query(cls).filter(cls.radio_name == radio_name).one_or_none()
            latest_live.track = track_new
            if latest_live.valid_till > datetime.now():
                latest_live.check_within = (latest_live.valid_till - latest_live.start_date).seconds + 1
            else:
                latest_live.check_within = 15
            latest_live.need_to_wait = False
            cls.session.close()

            return {'success': True, 'updated': True, 'result': latest_live}

