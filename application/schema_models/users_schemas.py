from flask_restx import Namespace, fields
from application.schema_models.validators import current_year, date_regx_format

users_schemas = Namespace('users_schemas', description='Input Output schemas for User')

user_setting = users_schemas.model('user_setting', {
    'user_setting': fields.String(description='user setting', max_length=20),
})


user_brief = users_schemas.model('user_brief', {
    'account_id': fields.String(description='user id'),
    'created_on': fields.DateTime(description='user creation name'),
    'display_name': fields.String(description='user display name'),
    'service_name': fields.String(description='name of music service'),
})

user_full = users_schemas.model('user_full', {
    'account_id': fields.String(description='user id', required=True),
    'account_uri': fields.String(description='user account link', required=False),
    'created_on': fields.DateTime(description='user creation name', required=False),
    'display_name': fields.String(description='user display name', required=False),
    'last_login': fields.DateTime(description='user creation name', required=False),
    'service_name': fields.String(description='name of music service', required=False),
    'radios': fields.String(description='name of music service', required=False),
    'settings': fields.String(description='user settings', required=False),
    # 'settings': fields.Raw(description='user settings', required=False),
    # add radios as nested field (import schema from radio)
    # booking_fields['end_dt'] = fields.Nested(namespace.model('timing_fields', timing_fields))

})

user_update = user_full

user_radios_update = users_schemas.model('user_radios_update', {
    'radios': fields.List(fields.String, description='user id')
})

make_import = users_schemas.model('make_import', {
    'radio_name': fields.String(required=True, max_length=20),
    'account_id': fields.String,
    'date': fields.String(pattern=date_regx_format, description=f'use format: dd-mm-{current_year}', max_length=10)
})
