from application.db_models import dbimport_db
from flask import request
from flask_restx import Namespace, Resource
from application.schema_models.dbimports_schemas import di_brief, di_full, di_num, di_num_per_radios
from application.schema_models.validators import validate_date_range, date_range_req, limit_req

dbimports_api = Namespace('DBImports', description='Imports of new tracks')


@dbimports_api.route('/')
class DBImports(Resource):

    @dbimports_api.marshal_list_with(di_brief)
    def get(self):
        """ List of all Imports of DB """
        return dbimport_db.DBImport.all()


@dbimports_api.route('/<import_date>')
@dbimports_api.response(404, 'Import not found')
@dbimports_api.param('import_date', 'Import date')
class DBImport(Resource):

    @dbimports_api.marshal_with(di_full)
    def get(self, import_date):
        """ Import info by date """
        return dbimport_db.DBImport.get_import_by_date(import_date)

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

    @dbimports_api.marshal_with(di_num)
    def get(self):
        """ Number of all Imports of DB """
        return dbimport_db.DBImport.get_imports_num()

@dbimports_api.route('/per_date')
class DBImports4Date(Resource):

    @dbimports_api.expect(date_range_req, limit_req, validate=True)
    @dbimports_api.marshal_list_with(di_brief)
    def get(self):
        """ Imports per date range """
        limit = request.args.get('limit')
        start, end = validate_date_range()
        return dbimport_db.DBImport.get_imports_per_date(start, end, end_id=limit)

@dbimports_api.route('/num/per_date')
class DBImports4DateNum(Resource):

    @dbimports_api.expect(date_range_req, validate=True)
    @dbimports_api.marshal_with(di_num)
    def get(self):
        """ Imports number per date range """
        start, end = validate_date_range()
        return dbimport_db.DBImport.get_imports_per_date_num(start, end)

@dbimports_api.route('/per_radios/num/')
class RTsReviewedNum(Resource):
    @dbimports_api.marshal_with(di_num_per_radios)
    def get(self):
        """ Number of reviewed Tracks of Radios """
        return {'result': dbimport_db.DBImport.get_imports_num_per_radios()}