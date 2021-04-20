from application.db_models import tracks_import
from application.db_models import radio
from flask import request
from flask_restx import Namespace, Resource
from application.schema_models import dbimports_schemas
from application.schema_models import validators

dbimports_api = Namespace('DBImports', description='Imports of new tracks')


@dbimports_api.route('/')
class DBImports(Resource):

    @dbimports_api.marshal_list_with(dbimports_schemas.di_brief)
    @dbimports_api.expect(validators.limit_req, validators.from_id_req, validate=True)
    def get(self):
        """ List of all Imports of DB """
        limit = request.args.get('limit')
        from_id_req = request.args.get('from_id')
        return tracks_import.TracksImport.get_imports(from_id_req, limit)

    @dbimports_api.response(500, 'Invalid values')
    @dbimports_api.expect(dbimports_schemas.make_import, validate=True)
    @dbimports_api.marshal_with(dbimports_schemas.di_full)
    def post(self):
        """ Import tracks for radio (adds all yesterdays tracks) """
        data = request.json or {}
        account_id = data.get('account_id', '')
        date = data.get('date')
        if date:
            date = validators.validate_date(date)
        radio_name = data.get('radio_name')
        return radio.Radio.update_radio_tracks(radio_name=radio_name, day=date, account_id=account_id)


@dbimports_api.route('/<import_date>')
@dbimports_api.response(404, 'Import not found')
@dbimports_api.param('import_date', 'Import date')
class DBImport(Resource):

    @dbimports_api.marshal_with(dbimports_schemas.di_full)
    def get(self, import_date):
        """ Import info by date """
        return tracks_import.TracksImport.get_import_by_date(import_date)


    # def delete(self, import_date):
    #     """ Delete Import by date """
    #     return {'result': dbimport_db.DBImport.get_radio_by_name(import_date)}
    #
    # def patch(self, import_date):
    #     """ Update Import by date """
    #     return {'result': dbimport_db.DBImport.get_radio_by_name(import_date)}
    #
    # def put(self, import_date):
    #     """ Add Import by date """
    #     return {'result': dbimport_db.DBImport.get_radio_by_name(import_date)}

@dbimports_api.route('/num')
class DBImportsNum(Resource):

    @dbimports_api.marshal_with(dbimports_schemas.di_num)
    def get(self):
        """ Number of all Imports of DB """
        return tracks_import.TracksImport.get_imports_num()

@dbimports_api.route('/per_date')
class DBImports4Date(Resource):

    @dbimports_api.expect(validators.date_range_req, validators.limit_req, validate=True)
    @dbimports_api.marshal_list_with(dbimports_schemas.di_brief)
    def get(self):
        """ Imports per date range """
        limit = request.args.get('limit')
        start, end = validators.validate_date_range()
        return tracks_import.TracksImport.get_imports_per_date(start, end, end_id=limit)

    @dbimports_api.response(500, 'Invalid values')
    @dbimports_api.expect(dbimports_schemas.make_import_per_range, validate=True)
    #@dbimports_api.marshal_with(dbimports_schemas.di_full)
    def post(self):
        """ Import tracks for radio (adds all yesterdays tracks) """
        data = request.json or {}
        account_id = data.get('account_id', '')
        start, end = validators.validate_date_range_post(data.get('start'), data.get('end'))
        radio_name = data.get('radio_name')
        return {'res': True}
        #return radio.Radio.update_radio_tracks(radio_name=radio_name, day=date, account_id=account_id)

@dbimports_api.route('/num/per_date')
class DBImports4DateNum(Resource):

    @dbimports_api.expect(validators.date_range_req, validate=True)
    @dbimports_api.marshal_with(dbimports_schemas.di_num)
    def get(self):
        """ Imports number per date range """
        start, end = validators.validate_date_range()
        return tracks_import.TracksImport.get_imports_per_date_num(start, end)

@dbimports_api.route('/per_radios/num/')
class RTsReviewedNum(Resource):
    @dbimports_api.marshal_with(dbimports_schemas.di_num_per_radios)
    def get(self):
        """ Number of reviewed Tracks of Radios """
        return {'result': tracks_import.TracksImport.get_imports_num_per_radios()}