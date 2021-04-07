from application.db_models import tracks_import
from flask_restx import Namespace, Resource
from flask import request
from application.schema_models.dbimports_schemas import di_num, di_brief
from application.schema_models.validators import validate_date_range, limit_req, radio_req, date_range_req

radio_imports_api = Namespace('Radio Imports', description='Imports of Radio')


@radio_imports_api.route('/')
class RI(Resource):

    @radio_imports_api.expect(limit_req, radio_req, validate=True)
    @radio_imports_api.marshal_list_with(di_brief)
    def get(self):
        """ List of Imports of Radio """
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        return tracks_import.TracksImport.get_imports_per_radio(radio_name, end_id=limit)

@radio_imports_api.route('/latest')
class RI(Resource):

    @radio_imports_api.expect(radio_req, validate=True)
    @radio_imports_api.marshal_with(di_brief)
    def get(self):
        """ Latest Import of Radio """
        radio_name = request.args.get('radio_name')
        return tracks_import.TracksImport.get_latest_import_for_radio(radio_name)


######### Number of tracks per radio #############
@radio_imports_api.route('/num')
class RINum(Resource):

    @radio_imports_api.expect(radio_req, validate=True)
    @radio_imports_api.marshal_with(di_num)
    def get(self):
        """ Number of Imports of Radio """
        radio_name = request.args.get('radio_name')
        return tracks_import.TracksImport.get_imports_num_per_radio(radio_name)


############## Radio Imports per date ###############
@radio_imports_api.route('/per_date')
class RI4Date(Resource):

    @radio_imports_api.expect(limit_req, radio_req, date_range_req, validate=True)
    @radio_imports_api.marshal_list_with(di_brief)
    def get(self):
        """ List of Imports of Radio per date range"""
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return tracks_import.TracksImport.get_imports_per_date_per_radio(start, end, radio_name, end_id=limit)


############## Radio Imports Number per date ###############
@radio_imports_api.route('/num/per_date')
class RI4DateNum(Resource):

    @radio_imports_api.expect(radio_req, date_range_req, validate=True)
    @radio_imports_api.marshal_with(di_num)
    def get(self):
        """ Number of Imports of Radio per date range"""
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return tracks_import.TracksImport.get_imports_per_date_per_radio_num(start, end, radio_name)

