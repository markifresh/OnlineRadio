from application.db_models import tracks_export
from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
from application.schema_models.validators import validate_date_range, date_range_req, limit_req, radio_req
from application.schema_models.spotifyexports_schemas import se_num, se_brief


radio_exports_api = Namespace('Radio Exports', description='Exports of Radio')

@radio_exports_api.route('/')
class RE(Resource):
    @radio_exports_api.expect(limit_req, radio_req, validate=True)
    def get(self):
        """ List of Exports of Radio """
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        return tracks_export.TracksExport.get_exports_per_radio(radio_name, end_id=limit)

@radio_exports_api.route('/latest')
class RE(Resource):
    @radio_exports_api.expect(radio_req, validate=True)
    @radio_exports_api.marshal_with(se_brief)
    def get(self):
        """ Latest Export of Radio """
        radio_name = request.args.get('radio_name')
        return tracks_export.TracksExport.get_latest_export_for_radio(radio_name)


######### Number of tracks per radio #############
@radio_exports_api.route('/num')
class RENum(Resource):

    @radio_exports_api.expect(radio_req, validate=True)
    @radio_exports_api.marshal_with(se_num)
    def get(self):
        """ Number of Exports of Radio """
        radio_name = request.args.get('radio_name')
        return tracks_export.TracksExport.get_exports_num_per_radio(radio_name)


############## Radio Exports per date ###############
@radio_exports_api.route('/per_date')
class RE4Date(Resource):

    @radio_exports_api.expect(limit_req, radio_req, date_range_req, validate=True)
    @radio_exports_api.marshal_list_with(se_brief)
    def get(self):
        """ List of Exports of Radio per date range"""
        limit = request.args.get('limit', '100')
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return tracks_export.TracksExport.get_exports_per_date_per_radio(start, end, radio_name, end_id=limit)


############## Radio Exports Number per date ###############
@radio_exports_api.route('/num/per_date')
class RE4DateNum(Resource):

    @radio_exports_api.expect(radio_req, date_range_req, validate=True)
    @radio_exports_api.marshal_with(se_num)
    def get(self):
        """ Number of Exports of Radio per date range"""
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return tracks_export.TracksExport.get_exports_per_date_per_radio_num(start, end, radio_name)

