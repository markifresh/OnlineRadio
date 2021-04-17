from application.db_models import user, tracks_import, tracks_export
from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flask import request
from application.schema_models import users_schemas, validators, dbimports_schemas, exports_schemas, tracks_schemas
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

@users_api.route('/<account_id>/tracks')
@users_api.param('account_id', 'Account ID of user')
class UserTracks(Resource):

    @users_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self, account_id):
        """ All users tracks (for all radios) """
        return user.User.get_user_tracks(account_id)



@users_api.route('/<account_id>/imports')
@users_api.param('account_id', 'Account ID of user')
class UserImports(Resource):

    @users_api.marshal_list_with(dbimports_schemas.di_brief)
    def get(self, account_id):
        """ User imports by ID """
        return user.User.get_user_imports(account_id)

@users_api.route('/<account_id>/imports/<radio_name>')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('radio_name', 'Name of radio')
class UserRadioImports(Resource):

    @users_api.marshal_list_with(dbimports_schemas.di_brief)
    def get(self, account_id, radio_name):
        """ All imports for radio for user """
        return user.User.get_user_imports_for_radio(account_id, radio_name)

@users_api.route('/<account_id>/imports/<radio_name>/tracks')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('radio_name', 'Name of radio')
class UserRadioImportsTracks(Resource):

    @users_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self, account_id, radio_name):
        """ All tracks of imports of radio of user """
        return user.User.get_user_imported_tracks_for_radio(account_id, radio_name)

@users_api.route('/<account_id>/exports')
@users_api.param('account_id', 'Account ID of user')
class UserExports(Resource):

    @users_api.marshal_list_with(exports_schemas.se_brief)
    def get(self, account_id):
        """ User exports by ID """
        return user.User.get_user_exports(account_id)


@users_api.route('/<account_id>/exports/<radio_name>')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('radio_name', 'Name of radio')
class UserRadioExports(Resource):

    @users_api.marshal_list_with(exports_schemas.se_brief)
    def get(self, account_id, radio_name):
        """ All exports for radio for user """
        return user.User.get_user_exports_for_radio(account_id, radio_name)

@users_api.route('/<account_id>/exports/<radio_name>/tracks')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('radio_name', 'Name of radio')
class UserRadioExportsTracks(Resource):

    @users_api.marshal_list_with(exports_schemas.se_brief)
    def get(self, account_id, radio_name):
        """ All tracks of exports of radio of user """
        return user.User.get_user_exported_tracks_for_radio(account_id, radio_name)
    # def delete(self, common_name):
    #     """ Delete track by name """
    #     return {'result': track_db.Track.get_track(common_name)}
    #
    # @tracks_api.expect(track_update, validate=True)
    # def put(self, common_name):
    #     """ Update track by name """
    #     return {'result': track_db.Track.get_track(common_name)}