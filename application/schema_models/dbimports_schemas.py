from flask_restx import Namespace, fields, reqparse, inputs
from datetime import datetime
from application.schema_models.validators import current_year, date_regx_format, time_regx_format, datetime_regx_format, date_datetime_regx_format

max_radio_name_length = 20

di_schemas = Namespace('di_schemas', description='Input Output schemas for DBImports')

di_brief = di_schemas.model('di_brief', {
    'import_date': fields.DateTime,
    'radio_name': fields.String,
    'num_tracks_added': fields.Integer
})

di_full = di_schemas.model('di_full', {
    'id': fields.Integer(required=True),
    'import_date': fields.DateTime(required=True),
    'num_tracks_requested': fields.Integer(required=True),
    'num_tracks_added': fields.Integer(required=True),
    'radio_name': fields.String(required=True),
    'import_duration': fields.Float(required=True),
    'exported': fields.Boolean,
    'reviewed': fields.Boolean
})

di_update = di_schemas.model('di_update', {
    'import_date': fields.DateTime(required=True),
    'radio_name': fields.String(required=True),
})

make_import = di_schemas.model('make_import', {
    'radio_name': fields.String(required=True, max_length=max_radio_name_length),
    'account_id': fields.String,
    'date': fields.String(pattern=date_regx_format, description=f'use format: dd-mm-{current_year}', max_length=10)
})

make_import_per_range = di_schemas.model('make_import', {
    'radio_name': fields.String(required=True, max_length=max_radio_name_length),
    'account_id': fields.String,
    'start_date': fields.String(required=True, pattern=date_datetime_regx_format, description=f'use format: dd-mm-{current_year}'),
    'end_date': fields.String(required=True, pattern=date_datetime_regx_format, description=f'use format: dd-mm-{current_year}')
})

post_result = di_schemas.model('post_result', {
    'success': fields.String,
    'for_date': fields.String,
    'import_date': fields.String,
    'import_duration': fields.Float(attribute='update_time_sec'),
    'total tracks number': fields.Integer,
    'num_tracks_requested': fields.Integer,
    'num_tracks_added': fields.Integer,
})


di_num = di_schemas.model('di_num', {'number': fields.Integer})
di_num_per_radios = di_schemas.model('di_num_per_radios', {'result': fields.Raw()})