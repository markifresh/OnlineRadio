from flask_restx import Namespace, fields, reqparse, inputs
from datetime import datetime
from application.schema_models.validators import current_year, date_regx_format, time_regx_format, datetime_regx_format



di_schemas = Namespace('di_schemas', description='Input Output schemas for DBImports')

di_brief = di_schemas.model('di_brief', {
    'import_date': fields.String,
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

make_import = di_schemas.model('make_import', {
    'radio_name': fields.String(required=True),
    'account_id': fields.String,
    'date': fields.String,
})

make_import_per_range = di_schemas.model('make_import', {
    'radio_name': fields.String(required=True),
    'account_id': fields.String,
    'start_date': fields.String(required=True, pattern=date_regx_format, description=f'use format: dd-mm-{current_year}'),
    'end_date': fields.String(required=True, pattern=datetime_regx_format, description=f'use format: dd-mm-{current_year}')
})



di_num = di_schemas.model('di_num', {'number': fields.Integer})
di_num_per_radios = di_schemas.model('di_num_per_radios', {'result': fields.Raw()})