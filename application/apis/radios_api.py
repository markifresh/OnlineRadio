from flask import request
from application.db_models import radio
from application.db_models import tracks_export
from flask_restx import Namespace, Resource, fields
from application.schema_models import radios_schemas


radios_api = Namespace('Radios', description='Methods of Radio')


@radios_api.route('/')
class Radios(Resource):

    @radios_api.marshal_list_with(radios_schemas.radio_brief)
    def get(self):
        """ List of all Radios of DB """
        return radio.Radio.all()

@radios_api.route('/<name>')
@radios_api.response(404, 'Radio not found')
@radios_api.param('name', 'Radio name')
class Radio(Resource):

    @radios_api.marshal_with(radios_schemas.radio_full)
    def get(self, name):
        """ Radio info by name """
        return radio.Radio.get_radio_by_name(name)


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
    def post(self):
        """ Update all radios tracks (adds all yesterdays tracks) """
        return radio.Radio.update_all_radios_tracks()


@radios_api.route('/<name>/import')
@radios_api.response(404, 'Radio not found')
class RadioUpdate(Resource):

    @radios_api.response(500, 'Invalid values')
    @radios_api.param('name', 'Radio name')
    @radios_api.expect(radios_schemas.radio_tracks_request, validate=True)
    @radios_api.marshal_with(radios_schemas.radio_tracks_update)
    def post(self, name):
        """ Import tracks for radio (adds all yesterdays tracks) """
        data = request.json
        account_id = data.get('account_id', '')
        date = data.get('date')
        return radio.Radio.update_radio_tracks(radio_name=name, day=date, account_id=account_id)

    # @radios_api.response(500, 'Invalid values')
    # @radios_api.marshal_with(radios_schemas.radio_tracks_update)
    # def post(self):
    #     """ Modify user """
    #     return user.User.user_update(request.json)


@radios_api.route('/update/radios_list')
class RadiosListUpdate(Resource):

    @radios_api.marshal_with(radios_schemas.radios_list_update)
    def get(self):
        """ Update radios list (checks if new radios available and add them to DB) """
        return radio.Radio.update_radios_list()


@radios_api.route('/<name>/export')
@radios_api.param('name', 'Radio name')
class RadioExport(Resource):

    @radios_api.marshal_with(radios_schemas.radio_tracks_export)
    def get(self, name):
        """ Exports tracks of radio to Spotify """
        return radio.Radio.export_tracks(name)

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
