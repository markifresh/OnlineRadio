from application.db_models import spotifyexport_db as se_db
from flask_restx import Namespace, Resource
from flask import request
from application.schema_models.spotifyexports_schemas import se_brief, se_full, se_num
from application.schema_models.validators import validate_date_range, date_range_req, limit_req

spotifyexports_api = Namespace('SpotifyExports', description='Exports of new tracks')


@spotifyexports_api.route('/')
class SEs(Resource):

    @spotifyexports_api.marshal_list_with(se_brief)
    def get(self):
        """ List of all Exports of DB """
        return se_db.SpotifyExport.all()


@spotifyexports_api.route('/<export_date>')
@spotifyexports_api.param('export_date', 'Export date')
class SE(Resource):

    @spotifyexports_api.marshal_with(se_full)
    def get(self, export_date):
        """ Export info by date """
        return se_db.SpotifyExport.get_export_by_date(export_date)

    # def delete(self, export_date):
    #     """ Delete Export by date """
    #     return {'result': se_db.SpotifyExport.get_radio_by_name(export_date)}
    #
    # def patch(self, export_date):
    #     """ Update Export by date """
    #     return {'result': se_db.SpotifyExport.get_radio_by_name(export_date)}
    #
    # def put(self, export_date):
    #     """ Add Export by date """
    #     return {'result': se_db.SpotifyExport.get_radio_by_name(export_date)}


@spotifyexports_api.route('/num')
class SENum(Resource):

    @spotifyexports_api.marshal_with(se_num)
    def get(self):
        """ Number of all Exports of DB """
        return se_db.SpotifyExport.get_exports_num()
    
    
@spotifyexports_api.route('/per_date')
class SE4Date(Resource):

    @spotifyexports_api.expect(date_range_req, limit_req, validate=True)
    @spotifyexports_api.marshal_list_with(se_brief)
    def get(self):
        """ Exports per date range """
        limit = request.args.get('limit')
        start, end = validate_date_range()
        return se_db.SpotifyExport.get_exports_per_date(start, end, end_id=limit)

@spotifyexports_api.route('/num/per_date')
class SE4DateNum(Resource):

    @spotifyexports_api.expect(date_range_req, validate=True)
    @spotifyexports_api.marshal_with(se_num)
    def get(self):
        """ Exports number per date range """
        start, end = validate_date_range()
        return se_db.SpotifyExport.get_exports_per_date_num(start, end)
