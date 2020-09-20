import json
import config
from flask import Flask, request, redirect, g, render_template
from flask_sqlalchemy import SQLAlchemy
# from flask_restplus import Api, Resource, fields
from db_models import BaseExtended
from db_models.dbimport_db import DBImport
from db_models.track_db import Track
from db_models.spotifyexport_db import SpotifyExport
from db_models.radio_db import Radio
import requests
from urllib.parse import quote
from blueprints import radios_page
import blueprints

import secret_data
from requests import get

environment_config = config.all_environments['development']

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.



# https://towardsdatascience.com/working-with-apis-using-flask-flask-restplus-and-swagger-ui-7cf447deda7f
# https://towardsdatascience.com/the-right-way-to-build-an-api-with-python-cd08ab285f8f
# https://towardsdatascience.com/visualizing-data-with-roughviz-js-77b8f96331e9
# https://towardsdatascience.com/building-a-weather-app-using-openweathermap-and-flask-ed7402239d83
# https://towardsdatascience.com/creating-a-beautiful-web-api-in-python-6415a40789af
# http://michal.karzynski.pl/blog/2016/06/19/building-beautiful-restful-apis-using-flask-swagger-ui-flask-restplus/

app = Flask(__name__)
app.register_blueprint(radios_page.radios_page)

# api = Api(app,
#           version='1.0',
#           title='Sample Book API',
#           description='A simple Book API',
#           doc=environment_config["swagger-url"])

# app.register_blueprint(simple_page, url_prefix='/pages') # register blueprint to other location

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{config.db_location}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#  Client Keys
CLIENT_ID = secret_data.spotify_api_id
CLIENT_SECRET = secret_data.spotify_api_key

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

# @appe.errorhandler(404)
# def page_not_found(e):
#     return render_template('pages/404.html')


@app.route("/")
def index():
    # Auth Step 1: Authorization
    from urllib.parse import urlencode
    params = urlencode({
        'client_id': secret_data.spotify_api_id,
        'scope': 'playlist-read-private playlist-modify-private',
        # 'scope': ['user-read-email', 'user-follow-read'],
        'redirect_uri': 'http://127.0.0.1:8080/callback/q',
        'response_type': 'code'
    })
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, params)
    print(auth_url)
    get(auth_url)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    return response_data
    # access_token = response_data["access_token"]
    # refresh_token = response_data["refresh_token"]
    # token_type = response_data["token_type"]
    # expires_in = response_data["expires_in"]


    # # Auth Step 6: Use the access token to access Spotify API
    # authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    #
    # # Get profile data
    # user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    # profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    # profile_data = json.loads(profile_response.text)
    #
    # # Get user playlist data
    # playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    # playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    # playlist_data = json.loads(playlists_response.text)
    #
    # # Combine profile and playlist data to display
    # display_arr = [profile_data] + playlist_data["items"]
    # return render_template("index.html", sorted_array=display_arr)

@app.route('/statistics')
def statistics():
    radios = Radio.get_all_objects()
    radios_tracks_num = [{radio.name: radio.get_tracks_number()} for radio in radios]
    return str(radios_tracks_num)

if __name__ == "__main__":
    app.run(debug=environment_config['debug'],
            port=environment_config['port'])