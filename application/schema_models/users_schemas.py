from flask_restx import Namespace, fields

users_schemas = Namespace('users_schemas', description='Input Output schemas for User')

user_brief = users_schemas.model('user_brief', {
    'account_id': fields.String(description='user id'),
    'created_on': fields.DateTime(description='user creation name'),
    'display_name': fields.String(description='user display name'),
    'service_name': fields.String(description='name of music service'),
})

user_full = users_schemas.model('user_full', {
    'account_id': fields.String(description='user id', required=True),
    'account_uri': fields.String(description='user account link'),
    'created_on': fields.DateTime(description='user creation name'),
    'display_name': fields.String(description='user display name'),
    'last_login': fields.DateTime(description='user creation name'),
    'service_name': fields.String(description='name of music service'),
    'setting': fields.Raw(description='user settings'),
})

user_update = user_full