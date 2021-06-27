from application.db_models import user, tracks_import, tracks_export, radio
from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flask import request
from application.schema_models import users_schemas, validators, dbimports_schemas, exports_schemas, tracks_schemas, radios_schemas
from datetime import datetime, timedelta
from config import APIConfig, read_date_time_format

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

@users_api.route('/<account_id>/tracks/liked')
@users_api.param('account_id', 'Account ID of user')
class UserLikedTracks(Resource):

    @users_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self, account_id):
        """ All users liked tracks (for all radios) """
        return user.User.get_user_liked_tracks(account_id)

    @users_api.marshal_list_with(tracks_schemas.track_brief)
    def post(self, account_id):
        """ Mark tracks as liked """
        tracks_ids = request.json or {}
        tracks_ids = tracks_ids.get('tracks_ids')
        return user.User.liked_tracks_add(account_id, tracks_ids)

    @users_api.marshal_list_with(tracks_schemas.track_brief)
    def delete(self, account_id):
        """ Remove tracks from liked """
        tracks_ids = request.json or {}
        tracks_ids = tracks_ids.get('tracks_ids')
        return user.User.liked_tracks_remove(account_id, tracks_ids)

@users_api.route('/<account_id>/imports')
@users_api.param('account_id', 'Account ID of user')
class UserImports(Resource):

    @users_api.marshal_list_with(dbimports_schemas.di_full)
    def get(self, account_id):
        """ User imports by ID """
        return user.User.get_user_imports(account_id)

    @users_api.marshal_with(dbimports_schemas.post_result)
    def post(self, account_id):
        """ Import tracks for radio (adds all yesterdays tracks) """
        data = request.json or {}
        date = data.get('date', datetime.now().date() - timedelta(days=1))
        radio_name = data.get('radio_name')
        return {}

@users_api.route('/<account_id>/imports/<import_date>')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('import_date', 'date of import')
class UserImport(Resource):

    @users_api.marshal_with(dbimports_schemas.di_full)
    def get(self, account_id, import_date):
        """ User import for date """
        return user.User.get_user_import(account_id, import_date)

@users_api.route('/<account_id>/imports/<radio_name>')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('radio_name', 'Name of radio')
class UserRadioImports(Resource):

    @users_api.marshal_list_with(dbimports_schemas.di_brief)
    def get(self, account_id, radio_name):
        """ All imports for radio for user """
        return user.User.get_user_imports_for_radio(account_id, radio_name)

    @users_api.marshal_list_with(dbimports_schemas.di_brief)
    def post(self, account_id, radio_name):
        """ All imports for radio for user """
        validators.validate_radio_name(radio_name)
        date = datetime.now().date() - timedelta(days=1)
        return radio.Radio.update_radio_tracks(radio_name=radio_name, start_date=date, account_id=account_id)

@users_api.route('/<account_id>/imports/unexported')
@users_api.param('account_id', 'Account ID of user')
class UserImportsUnexported(Resource):

    @users_api.marshal_list_with(dbimports_schemas.di_brief)
    def get(self, account_id):
        """ User unexported imports by ID """
        return user.User.get_user_unexported_imports(account_id)

@users_api.route('/<account_id>/imports/unexported/<radio_name>')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('radio_name', 'Name of radio')
class UserImportsUnexportedForRadio(Resource):

    @users_api.marshal_list_with(dbimports_schemas.di_brief)
    def get(self, account_id, radio_name):
        """ User unexported imports for radios by ID """

        validators.validate_radio_name(radio_name)
        return user.User.get_user_unexported_imports_by_radio(account_id, radio_name)

@users_api.route('/<account_id>/imports/<import_date>/tracks')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('import_date', 'Date of import')
class UserImportTracks(Resource):

    @users_api.marshal_list_with(tracks_schemas.track_table)
    def get(self, account_id, import_date):
        """ All tracks of imports of radio of user """
        import_date = validators.validate_date(import_date)
        validators.validate_user(account_id)
        current_user = user.User.get_user(account_id)
        user_liked_tracks = [int(cur_track) for cur_track in current_user.liked_tracks.split(',')]
        import_tracks = tracks_import.TracksImport.get_import_tracks(import_date, current_user.service_name)
        for import_track in import_tracks:
            if import_track.id in user_liked_tracks:
                import_track.liked = True
            else:
                import_track.liked = False
        return import_tracks


@users_api.route('/<account_id>/imports/<import_date>/tracks/<tracks_id>')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('import_date', 'Date of import')
class UserImportTrackDelete(Resource):

    @users_api.marshal_list_with(tracks_schemas.track_brief)
    def delete(self, account_id, import_date):
        tracks_ids = request.json or {}
        tracks_ids = tracks_ids.get('tracks_ids')
        return user.User.import_tracks_remove(account_id, import_date, tracks_ids)

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

    def post(self, account_id):
        """ User export unexported imports to Music Service """
        imports_ids = user.User.get_user_unexported_imports(account_id)
        imports_ids = [res['id'] for res in imports_ids]
        return {'result': tracks_export.TracksExport.export_imports(imports_ids)}

@users_api.route('/<account_id>/exports/<radio_name>')
@users_api.param('account_id', 'Account ID of user')
@users_api.param('radio_name', 'Name of radio')
class UserRadioExports(Resource):

    @users_api.marshal_list_with(exports_schemas.se_brief)
    def get(self, account_id, radio_name):
        """ All exports for radio for user """
        return user.User.get_user_exports_for_radio(account_id, radio_name)

    def post(self, account_id, radio_name):
        """ User export unexported imports to Music Service for Radio """

        imports_ids = user.User.get_user_unexported_imports_by_radio(account_id, radio_name)
        imports_ids = [res.id for res in imports_ids]
        results = tracks_export.TracksExport.export_imports(imports_ids)
        if not results['success']:
            return {'success': False, 'result': str(results)}

        num_tracks_requested = 0
        num_tracks_added = 0
        for result in results['result']:
            if result['success']:
                num_tracks_requested += result['export_data']['num_tracks_requested']
                num_tracks_added += result['export_data']['num_tracks_added']

        return {'success': results['success'],
                'num_tracks_requested': num_tracks_requested,
                'num_tracks_added': num_tracks_added,
                'date': datetime.now().strftime(read_date_time_format)}

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

@users_api.route('/<account_id>/radios')
@users_api.param('account_id', 'Account ID of user')
class UserRadios(Resource):

    @users_api.marshal_list_with(radios_schemas.radio_brief)
    def get(self, account_id):
        """ All radios of user """
        return user.User.get_user_radios(account_id)

    @users_api.expect(radios_schemas.radio_name, validate=True)
    def put(self, account_id):
        """ Add user radios """
        radio_name = request.json.get('radio_name')
        validators.validate_radio_name(radio_name)
        return user.User.add_user_radio(account_id, radio_name)

    @users_api.expect(radios_schemas.radio_name, validate=True)
    def delete(self, account_id):
        """ Delete user radios """
        radio_name = request.json.get('radio_name')
        validators.validate_radio_name(radio_name)
        return user.User.delete_user_radio(account_id, radio_name)

@users_api.route('/<account_id>/settings')
@users_api.param('account_id', 'Account ID of user')
class UserSettings(Resource):

    def get(self, account_id):
        """ All Settings of user """
        return {'result': user.User.get_user_settings(account_id)}

    @users_api.expect(users_schemas.user_setting, validate=True)
    def put(self, account_id):
        """ Add user setting """
        user_setting = request.json.get('user_setting')
        validators.validate_setting(user_setting)
        return user.User.add_user_setting(account_id, user_setting)

    @users_api.expect(users_schemas.user_setting, validate=True)
    def delete(self, account_id):
        """ Delete user setting """
        user_setting = request.json.get('user_setting')
        validators.validate_setting(user_setting)
        return user.User.delete_user_setting(account_id, user_setting)
