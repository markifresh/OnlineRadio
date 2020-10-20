from flask import redirect, url_for, Blueprint, request, current_app, session
from config import SpotifyConfig as auth_config
from json import loads as json_loads
from requests import post as req_post
from urllib.parse import urlencode

oauth_page = Blueprint('oauth', __name__, template_folder='templates')


@oauth_page.route('/')
def spotify_redirect():
    # Auth Step 1: Authorization
    session['pre_auth_page'] = request.referrer
    params = urlencode({
        'client_id': auth_config.CLIENT_ID,
        'scope': auth_config.SCOPE,
        'redirect_uri': url_for('oauth.callback', _external=True),
        'response_type': 'code'
    })

    auth_url = f'{auth_config.SPOTIFY_AUTH_URL}/?{params}'
    return redirect(auth_url)


@oauth_page.route('/callback')
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        'grant_type': 'authorization_code',
        'code': str(auth_token),
        'redirect_uri': url_for('oauth.callback', _external=True),
        'client_id': auth_config.CLIENT_ID,
        'client_secret': auth_config.CLIENT_KEY,
    }
    post_request = req_post(auth_config.SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json_loads(post_request.text)
    session['oauth'] = response_data
    print(session['oauth'])
    from application.workers import spotifyWorker
    return redirect(session['pre_auth_page'] )

    # add in localStorage / session: time of expiration.
    # If expired, redirect to auth ling again or use refresh token
    # {
    #     "access_token": "BQBTjGjSe6e9R8Clf5HDcnhksApS7JCi7SiO1HW0mbTwoZWgiqVylT6muT6hCSvjO9zR8VgvQve2hPMlVOHeHK4Tj1niTFDcMcCX1cd6NK0eGUMqqyYf-6iwjFKbRiRewPPiv36JkNntH_Uyh4G6yWlqxNv0LXdtWjeD7iVzzKpkPpNnr28671PUyMk5_KGCj6woEEKu5zDxMMDvLyFz2KJL2HKoWYc",
    #     "expires_in": 3600,
    #     "refresh_token": "AQAGhFKU_t_pwpIqlj9QA-XUqARapBxaIipb90D7NIaNALd8aeHUg2jTcKO5sdezujmeb2fvJexgA9PsWHu4UNBh1-JSdqtc2Px_Y9LRByBD1a5X34lCvA7deQHxbL0U6XM",
    #     "scope": "playlist-modify-private playlist-modify-public",
    #     "token_type": "Bearer"
    # }


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
