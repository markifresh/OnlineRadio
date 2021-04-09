from application.db_models import user
from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flask import request
from application.schema_models import users_schemas
from application.schema_models import validators
from datetime import datetime
from config import APIConfig

users_api = Namespace('Users', description='Methods of Users')
envelope = APIConfig.api_envelope


@users_api.route('/')
class Users(Resource):
    @users_api.expect(validators.limit_req, validators.from_id_req, validate=True)
    @users_api.marshal_list_with(users_schemas.user_brief, envelope=envelope)
    def get(self):
        """ List of Users of DB """
        limit = request.args.get('limit')
        from_id_req = request.args.get('from_id')
        return user.User.get_all_users(start_id=from_id_req, end_id=from_id_req+limit)
        # return {'result': track_db.Track.get_tracks_all(start=0, end=int(limit))}

    @users_api.response(500, 'Invalid values')
    @users_api.marshal_with(users_schemas.user_full)
    @users_api.expect(users_schemas.user_update, validate=True)
    def put(self):
        """ Modify user """
        return user.User.user_update(request.json)

@users_api.route('/<account_id>')
@users_api.param('account_id', 'Account ID of user')
class User(Resource):

    @users_api.marshal_with(users_schemas.user_full)
    def get(self, account_id):
        """ Account info by ID """
        return user.User.get_user(account_id)

    # def delete(self, common_name):
    #     """ Delete track by name """
    #     return {'result': track_db.Track.get_track(common_name)}
    #
    # @tracks_api.expect(track_update, validate=True)
    # def put(self, common_name):
    #     """ Update track by name """
    #     return {'result': track_db.Track.get_track(common_name)}