from application.db_models import track
from flask_restx import Namespace, Resource, fields, reqparse
from flask import request
from application.schema_models.validators import date_range_req, validate_date_range, radio_req, limit_req
from application.schema_models import tracks_schemas


radio_tracks_api = Namespace('Radio Tracks', description='Tracks of Radio')


@radio_tracks_api.route('/')
class RT(Resource):
    @radio_tracks_api.expect(limit_req, radio_req, validate=True)
    @radio_tracks_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self):
        """ List of Tracks of Radio """
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        return track.Track.get_tracks_per_radio(radio_name, end_id=limit)

@radio_tracks_api.route('/reviewed')
class RTReviewed(Resource):
    @radio_tracks_api.expect(limit_req, radio_req, validate=True)
    @radio_tracks_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self):
        """ List of reviewed Tracks of Radio """
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        return track.Track.get_tracks_reviewed_per_radio(radio_name, end_id=limit)

@radio_tracks_api.route('/not_reviewed')
class RTNotReviewed(Resource):
    @radio_tracks_api.expect(limit_req, radio_req, validate=True)
    @radio_tracks_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self):
        """ List of not reviewed Tracks of Radio """
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        return track.Track.get_tracks_reviewed_not_per_radio(radio_name, end_id=limit)

######### Number of tracks per radio #############
@radio_tracks_api.route('/num')
class RTNum(Resource):
    @radio_tracks_api.expect(radio_req, validate=True)
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_num)
    def get(self):
        """ Number of Tracks of Radio """
        radio_name = request.args.get('radio_name')
        return track.Track.get_tracks_per_radio_num(radio_name)

@radio_tracks_api.route('/num/reviewed')
class RTReviewedNum(Resource):
    @radio_tracks_api.expect(radio_req, validate=True)
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_num)
    def get(self):
        """ Number of reviewed Tracks of Radio """
        radio_name = request.args.get('radio_name')
        return track.Track.get_tracks_reviewed_per_radio_num(radio_name)

@radio_tracks_api.route('/num/not_reviewed')
class RTNotReviewedNum(Resource):
    @radio_tracks_api.expect(radio_req, validate=True)
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_num)
    def get(self):
        """ Number of not reviewed Tracks of Radio """
        radio_name = request.args.get('radio_name', )
        return track.Track.get_tracks_reviewed_not_per_radio_num(radio_name)


############## Radio Tracks per date ###############
@radio_tracks_api.route('/per_date')
class RT4Date(Resource):
    @radio_tracks_api.expect(limit_req, radio_req, date_range_req, validate=True)
    @radio_tracks_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self):
        """ List of Tracks of Radio per date range"""
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return track.Track.get_tracks_per_date_per_radio(start_date=start, end_date=end, radio_name=radio_name,
                                                         end_id=limit)

@radio_tracks_api.route('/per_date/reviewed')
class RT4DateReviewed(Resource):
    @radio_tracks_api.expect(limit_req, radio_req, date_range_req, validate=True)
    @radio_tracks_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self):
        """ List of reviewed Tracks of Radio per date range """
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return track.Track.get_tracks_per_date_reviewed_per_radio(start_date=start, end_date=end,
                                                                  radio_name=radio_name, end_id=limit)

@radio_tracks_api.route('/per_date/not_reviewed')
class RT4DateNotReviewed(Resource):
    @radio_tracks_api.expect(limit_req, radio_req, date_range_req, validate=True)
    @radio_tracks_api.marshal_list_with(tracks_schemas.track_brief)
    def get(self):
        """ List of not reviewed Tracks of Radio per date range """
        limit = request.args.get('limit')
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return track.Track.get_tracks_per_date_reviewed_not_per_radio(start_date=start, end_date=end,
                                                                      radio_name=radio_name, end_id=limit)


############## Radio Tracks Number per date ###############
@radio_tracks_api.route('/num/per_date')
class RT4DateNum(Resource):
    @radio_tracks_api.expect(radio_req, date_range_req, validate=True)
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_num)
    def get(self):
        """ Number of Tracks of Radio per date range"""
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return track.Track.get_tracks_per_date_per_radio_num(start_date=start, end_date=end, radio_name=radio_name)

@radio_tracks_api.route('/num/per_date/reviewed')
class RT4DateReviewedNum(Resource):
    @radio_tracks_api.expect(radio_req, date_range_req, validate=True)
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_num)
    def get(self):
        """ Number of reviewed Tracks of Radio per date range """
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return track.Track.get_tracks_per_date_reviewed_num_per_radio(start_date=start, end_date=end,
                                                                      radio_name=radio_name)

@radio_tracks_api.route('/num/per_date/not_reviewed')
class RT4DateNotReviewedNum(Resource):
    @radio_tracks_api.expect(radio_req, date_range_req, validate=True)
    def get(self):
        """ Number of not reviewed Tracks of Radio per date range """
        radio_name = request.args.get('radio_name')
        start, end = validate_date_range()
        return track.Track.get_tracks_per_date_reviewed_not_num_per_radio(start_date=start, end_date=end,
                                                                          radio_name=radio_name)

@radio_tracks_api.route('/per_radios/num')
class RTsNotReviewedNum(Resource):
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_radios_num)
    def get(self):
        """ Number of not reviewed Tracks of Radios """
        return {'result': track.Track.get_tracks_per_radios_num()}

@radio_tracks_api.route('/per_radios/num/not_reviewed')
class RTsNotReviewedNum(Resource):
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_radios_num)
    def get(self):
        """ Number of not reviewed Tracks of Radios """
        return {'result': track.Track.get_tracks_reviewed_not_num_per_radios()}

@radio_tracks_api.route('/per_radios/num/reviewed')
class RTsReviewedNum(Resource):
    @radio_tracks_api.marshal_with(tracks_schemas.tracks_radios_num)
    def get(self):
        """ Number of reviewed Tracks of Radios """
        return {'result': track.Track.get_tracks_reviewed_num_per_radios()}