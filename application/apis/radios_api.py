from application.db_models import radio_db
from application.db_models import spotifyexport_db
from flask_restx import Namespace, Resource, fields
from application.schema_models import radios_schemas


radios_api = Namespace('Radios', description='Methods of Radio')


@radios_api.route('/')
class Radios(Resource):

    @radios_api.marshal_list_with(radios_schemas.radio_brief)
    def get(self):
        """ List of all Radios of DB """
        return radio_db.Radio.all()


@radios_api.route('/<name>')
@radios_api.response(404, 'Radio not found')
@radios_api.param('name', 'Radio name')
class Radio(Resource):

    @radios_api.marshal_with(radios_schemas.radio_full)
    def get(self, name):
        """ Radio info by name """
        return radio_db.Radio.get_radio_by_name(name)

    # def delete(self, name):
    #     """ Delete radio by name """
    #     return {'result': radio_db.Radio.get_radio_by_name(name)}
    #
    # @radios_api.expect(radios_schemas.radio_update)
    # def put(self, name):
    #     """ Update radio by name """
    #     return {'result': radio_db.Radio.get_radio_by_name(name)}
    #
    # @radios_api.expect(radios_schemas.radio_update)
    # def post(self, name):
    #     """ Add radio by name """
    #     return {'result': radio_db.Radio.get_radio_by_name(name)}


@radios_api.route('/update')
class RadiosUpdate(Resource):

    @radios_api.marshal_list_with(radios_schemas.radio_tracks_update)
    def get(self):
        """ Update all radios tracks (adds all yesterdays tracks) """
        return radio_db.Radio.update_all_radios_tracks()


@radios_api.route('/update/<name>')
@radios_api.response(404, 'Radio not found')
@radios_api.param('name', 'Radio name')
class RadioUpdate(Resource):

    @radios_api.marshal_with(radios_schemas.radio_tracks_update)
    def get(self, name):
        """ Update tracks for radio (adds all yesterdays tracks) """
        return radio_db.Radio.update_radio_tracks(name)


@radios_api.route('/update/radios_list')
class RadiosListUpdate(Resource):

    @radios_api.marshal_with(radios_schemas.radios_list_update)
    def get(self):
        """ Update radios list (checks if new radios available and add them to DB) """
        return radio_db.Radio.update_radios_list()


@radios_api.route('/export/<name>')
@radios_api.param('name', 'Radio name')
class RadioExport(Resource):

    @radios_api.marshal_with(radios_schemas.radio_tracks_export)
    def get(self, name):
        """ Exports tracks of radio to Spotify """
        return radio_db.Radio.export_tracks(name)

# @radios_api.route('/')
# class RadioLists(Resource):
#     @radios_api.doc('asdasdasdad')
#     def get(self):
#         """
#         Register a Resource for a given API Namespace
#         """
#         return {'result': radio_db.Radio.get_all_radios()}
#
#     # @radios_api.add_resource(urls='/update')
#     def patch(self):
#         """ Update radios list (checks if new radios available and add them to DB) """
#         return {'result': radio_db.Radio.update_radios_list()}

# @radios_api.route('/')
# class RadioApi(Resource):
#     @radios_api.doc()
#     def get(self):
#         """ returns list of radios """
#         return {'result': radio_db.Radio.get_all_radios()}
