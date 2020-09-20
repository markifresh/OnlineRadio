from db_models.extenders_for_db_models import BaseExtended
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship


class SpotifyExport(BaseExtended):
    unique_search_field = 'export_date'

    __tablename__ = 'spotifyExports'
    id = Column(Integer, primary_key=True)
    export_date = Column(Integer, Sequence('spotifyexports_export_date_seq'), unique=True)  # update_time in ms
    tracks = relationship('Track', lazy=True)
    radio_name = Column(String(20), ForeignKey('radios.name'), nullable=False)
    num_tracks_added = Column(Integer)
    num_tracks_requested = Column(Integer)
    num_tracks_reviewed = Column(Integer)

    # tracks_reviewed = tracs_ref

    def __repr__(self):
        return f"<spotifyExport({self.export_date}, {self.radio_name}, " \
               f"{self.num_tracks_requested} vs {self.num_tracks_added})>"
