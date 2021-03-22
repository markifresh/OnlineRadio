from application.db_models.dbimport_db import DBImport
DBImport.drop_table()
DBImport.create_tables()

from application.db_models.spotifyexport_db import SpotifyExport
SpotifyExport.drop_table()
SpotifyExport.create_tables()

from application.db_models.track_db import Track
Track.drop_table()
Track.create_tables()

from application.db_models.radio_db import Radio
res = Radio.update_radio_tracks_per_range('DJAM', '01-09-2020', '01-10-2020')