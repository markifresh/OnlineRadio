from flask_restx import Namespace, fields

users_schemas = Namespace('users_schemas', description='Input Output schemas for User')

user_settings = users_schemas.model('user_settings', {
    'a': fields.String(description='user settings'),

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
    'settings': fields.Nested(user_settings, description='user settings', required=False),
    # 'settings': fields.Raw(description='user settings', required=False),
    # add radios as nested field (import schema from radio)
    # booking_fields['end_dt'] = fields.Nested(namespace.model('timing_fields', timing_fields))

})

user_update = user_full
