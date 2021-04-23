from flask_restx import Namespace, fields

radios_schemas = Namespace('radios_schemas', description='Input Output schemas for Radio')

radio_brief = radios_schemas.model('radios_brief', {
    'name': fields.String(description='name of Radio'),
    'stream_url': fields.String,
    'id': fields.Integer
})

radio_full = radios_schemas.model('radio_full', {
    'id': fields.Integer,
    'name': fields.String,
    'url': fields.String,
    'created_on': fields.DateTime
})

radio_update = radios_schemas.model('radio_update', {
    'name': fields.String(required=True),
    'url': fields.String(required=True)
})

radios_list_update = radios_schemas.model('radios_list_update', {
    'success': fields.Boolean,
    'updated': fields.List(fields.String)
})

radio_tracks_update = radios_schemas.model('radio_tracks_update', {
    'success': fields.Boolean(default=False),
    'updated': fields.List(fields.String),
    'total tracks number': fields.Integer,
    'num_tracks_requested': fields.Integer,
    'num_tracks_added': fields.Integer,
    'update_time_sec': fields.Float,
    'import_date': fields.String
})

radio_tracks_export = radios_schemas.model('radio_tracks_export', {
    'success': fields.Boolean(default=False),
    # 'updated': fields.List(fields.String),
    'num_tracks_requested': fields.Integer,
    'num_tracks_exported': fields.Integer,
    'num_tracks_added': fields.Integer,
    'export_date': fields.String
})

radio_tracks_request = radios_schemas.model('radio_tracks_request', {
    'account_id': fields.String,
    'date': fields.String,
})

radio_tracks_request_per_range = radios_schemas.model('radio_tracks_request_per_range', {
    'account_id': fields.String,
    'start_date': fields.String,
    'end_date': fields.String
})

radio_name = radios_schemas.model('radio_name', {
    'radio_name': fields.String(required=True, max_length=10)
})