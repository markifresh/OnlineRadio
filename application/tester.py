from application.db_models.tracks_import import TracksImport
TracksImport.drop_table()
TracksImport.create_tables()

from application.db_models.tracks_export import TracksExport
TracksExport.drop_table()
TracksExport.create_tables()

from application.db_models.track import Track
Track.drop_table()
Track.create_tables()

from application.db_models.radio import Radio
res = Radio.update_radio_tracks_per_range('DJAM', '01-09-2020', '01-10-2020')