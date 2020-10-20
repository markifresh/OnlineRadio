from flask_restx import Namespace, fields

di_schemas = Namespace('di_schemas', description='Input Output schemas for DBImports')

di_brief = di_schemas.model('di_brief', {
    'import_date': fields.DateTime(required=True, description='Date of import'),
    'radio_name': fields.String,
    'num_tracks_added': fields.Integer
})

di_full = di_schemas.model('di_full', {
    'id': fields.Integer(required=True),
    'import_date': fields.DateTime(required=True),
    'num_tracks_requested': fields.Integer(required=True),
    'num_tracks_added': fields.Integer(required=True),
    'radio_name': fields.String(required=True),
    'import_duration': fields.Float(required=True)
})

di_update = di_schemas.model('di_update', {
    'import_date': fields.DateTime(required=True),
    'radio_name': fields.String(required=True),
})

di_num = di_schemas.model('di_num', {'number': fields.Integer})
di_num_per_radios = di_schemas.model('di_num_per_radios', {'result': fields.Raw()})