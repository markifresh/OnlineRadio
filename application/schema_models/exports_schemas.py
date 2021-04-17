from flask_restx import Namespace, fields

se_schemas = Namespace('se_schemas', description='Input Output schemas for SpotifyExports')

se_brief = se_schemas.model('se_brief', {
    'export_date': fields.String,
    'radio_name': fields.String,
    'num_tracks_exported': fields.Integer
})

se_full = se_schemas.model('se_full', {
    'id': fields.Integer(required=True),
    'export_date': fields.DateTime(required=True),
    'num_tracks_requested': fields.Integer(required=True),
    'num_tracks_added': fields.Integer(required=True),
    'num_tracks_reviewed': fields.Integer(required=True),
    'radio_name': fields.String(required=True)
})

se_update = se_schemas.model('se_update', {
    'export_date': fields.DateTime(required=True),
    'radio_name': fields.String(required=True),
})

se_num = se_schemas.model('se_num', {'number': fields.Integer})