from flask_restx import Namespace, fields

tracks_schemas = Namespace('tracks_schemas', description='Input Output schemas for Track')

track_brief = tracks_schemas.model('track_brief', {
    'artist': fields.String(description='title of a track'),
    'title': fields.String(description='artist of a track'),
    'id': fields.Integer(description='track id'),
})

track_full = tracks_schemas.model('track_full', {
    'artist': fields.String(required=True),
    'title': fields.String(required=True),
    'album_name': fields.String(required=False),
    'album_year': fields.String(required=False),
    'duration': fields.String(required=False),
    'play_date': fields.DateTime(required=False),
    'radio_name': fields.String(required=False),
    'db_import_date': fields.DateTime(required=False),
    'spotify_export_date': fields.String(required=False),
    'reviewed': fields.String(required=False),
    'in_spotify': fields.String(required=False),
    'genre': fields.String(required=False),
    'created_on': fields.DateTime(required=False),
    'ms_id': fields.String(required=False),
})

track_table = tracks_schemas.model('track_table', {
    'id': fields.Integer(required=True),
    'artist': fields.String(required=True),
    'title': fields.String(required=True),
    'rank': fields.Integer(description='rank of track based on Deezer', required=True),
    'ms_id': fields.String(description='id of track in Music Service', required=False),
    'play_date': fields.DateTime(description='when track was played'),
    'liked': fields.Boolean(description='if track was liked')
})

track_update = track_full
tracks_num = tracks_schemas.model('tracks_num', {'number': fields.Integer})

tracks_radios_num = tracks_schemas.model('tracks_radios_num', {'result': fields.Raw()})