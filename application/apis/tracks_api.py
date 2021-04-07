from application.db_models import track
from flask_restx import Namespace, Resource, fields, reqparse, inputs
from flask import request
from application.schema_models.tracks_schemas import *
from datetime import datetime
from application.schema_models.validators import validate_date_range, date_range_req, limit_req, from_id_req

# pagination_arguments.add_argument('page', type=int, required=False)
# pagination_arguments.add_argument('per_page', type=int, required=False, choices=[5, 10, 20, 30, 40, 50], default=10)
# pagination_arguments.add_argument('multiple', type=int, action='append', required=True)
# pagination_arguments.add_argument('radio_ids', choices=[5, 10, 20, 30, 40, 50])


tracks_api = Namespace('Tracks', description='Methods of Tracks')


@tracks_api.route('/')
class Tracks(Resource):
    @tracks_api.expect(limit_req, from_id_req, validate=True)
    @tracks_api.marshal_list_with(track_brief)
    def get(self):
        """ List of Tracks of DB """
        limit = request.args.get('limit')
        from_id_req = request.args.get('from_id')
        return track.Track.get_tracks(start_id=from_id_req, end_id=limit)
        # return {'result': track_db.Track.get_tracks_all(start=0, end=int(limit))}

    @tracks_api.expect(track_update, validate=True)
    def post(self, common_name):
        """ Add track """
        return {'result': track.Track.get_track(common_name)}

@tracks_api.route('/<common_name>')
# @tracks_api.response(404, 'Track not found')
@tracks_api.param('common_name', 'Common name of a track')
class Track(Resource):

    @tracks_api.marshal_with(track_full)
    def get(self, common_name):
        """ Track info by name """
        return track.Track.get_track(common_name)

    # def delete(self, common_name):
    #     """ Delete track by name """
    #     return {'result': track_db.Track.get_track(common_name)}
    #
    # @tracks_api.expect(track_update, validate=True)
    # def put(self, common_name):
    #     """ Update track by name """
    #     return {'result': track_db.Track.get_track(common_name)}


@tracks_api.route('/artists')
class Artists(Resource):
    @tracks_api.expect(limit_req, from_id_req, validate=True)
    def get(self):
        """ List of all Artists of DB """
        limit_req = request.args.get('limit')
        from_id_req = request.args.get('from_id')
        return track.Track.get_artists(from_id_req, limit_req)

@tracks_api.route('/artists/<artist_name>')
# @tracks_api.response(404, 'Artist not found')
@tracks_api.param('artist_name', 'Name of an artist')
class ArtistTrack(Resource):
    @tracks_api.expect(limit_req, from_id_req, validate=True)
    @tracks_api.marshal_list_with(track_brief)
    def get(self, artist_name):
        """ List artist's tracks """
        limit_req = request.args.get('limit')
        from_id_req = request.args.get('from_id')
        return track.Track.get_tracks_per_artist(artist=artist_name, start_id=from_id_req, end_id=limit_req)

@tracks_api.route('/artists/num')
class ArtistisNumber(Resource):

    def get(self):
        """ Number of artists in DB """
        return track.Track.get_artist_num()

@tracks_api.route('/reviewed')
class ReviewedTracks(Resource):
    @tracks_api.marshal_list_with(track_brief)
    @tracks_api.expect(limit_req, validate=True)
    def get(self):
        """ Reviewed tracks in DB """
        limit = request.args.get('limit')
        return track.Track.get_tracks_reviewed(end_id=limit)

@tracks_api.route('/not_reviewed')
class NotReviewedTracks(Resource):
    @tracks_api.expect(limit_req, validate=True)
    @tracks_api.marshal_list_with(track_brief)
    def get(self):
        """ Not reviewed tracks in DB """
        limit = request.args.get('limit')
        return track.Track.get_tracks_reviewed_not(end_id=limit)

############ Tracks Number #################
@tracks_api.route('/num')
class TracksNumber(Resource):

    def get(self):
        """ Number of tracks in DB """
        return track.Track.get_tracks_num()


@tracks_api.route('/num/reviewed')
class ReviewedTracksNumber(Resource):

    def get(self):
        """ Number of reviewed tracks in DB """
        return {'result': track.Track.get_tracks_reviewed_num()}


@tracks_api.route('/num/not_reviewed')
class NotReviewedTracksNumber(Resource):

    def get(self):
        """ Number of NOT reviewed tracks in DB """
        return {'result': track.Track.get_tracks_reviewed_not_num()}


########### Tracks per date #################

@tracks_api.route('/per_date')
class Tracks4Date(Resource):
    @tracks_api.marshal_list_with(track_brief)
    @tracks_api.expect(date_range_req, limit_req, validate=True)
    def get(self):
        """ Tracks per date range """
        limit = request.args.get('limit')
        start, end = validate_date_range()
        return track.Track.get_tracks_per_date(start, end, end_id=limit)


@tracks_api.route('/per_date/reviewed')
class Tracks4DateReviewed(Resource):
    @tracks_api.expect(date_range_req, limit_req, validate=True)
    def get(self):
        """ Reviewed Tracks per date range """
        limit = request.args.get('limit')
        start, end = validate_date_range()

        return {'result': track.Track.get_tracks_per_date_reviewed(start, end, end_id=limit)}

@tracks_api.route('/per_date/not_reviewed')
class Tracks4DateNotReviewed(Resource):
    @tracks_api.expect(date_range_req, limit_req, validate=True)
    def get(self):
        """ Not Reviewed Tracks per date range """
        limit = request.args.get('limit')
        start, end = validate_date_range()

        return {'result': track.Track.get_tracks_per_date_reviewed_not(start, end, end_id=limit)}

########### Tracks number per date #################
@tracks_api.route('/num/per_date')
class Tracks4DateNum(Resource):
    @tracks_api.expect(date_range_req, validate=True)
    def get(self):
        """ Tracks number per date range """
        start, end = validate_date_range()

        return {'result': track.Track.get_tracks_per_date_num(start, end)}


@tracks_api.route('/num/per_date/reviewed')
class Tracks4DateReviewedNum(Resource):
    @tracks_api.expect(date_range_req, validate=True)
    def get(self):
        """ Reviewed Tracks number per date range """
        start, end = validate_date_range()

        return {'result': track.Track.get_tracks_per_date_reviewed_num(start, end)}


@tracks_api.route('/num/per_date/not_reviewed')
class Tracks4DateNotReviewedNum(Resource):
    @tracks_api.expect(date_range_req, validate=True)
    def get(self):
        """ Not Reviewed Tracks number per date range """
        start, end = validate_date_range()

        return {'result': track.Track.get_tracks_per_date_reviewed_not_num(start, end)}


