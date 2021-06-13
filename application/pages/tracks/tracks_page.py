from flask import Blueprint, render_template, session
from application.db_models.track import Track
from flask import current_app as app
# from application.apis.radios.root import list_radios
from flask_login import login_required

tracks = Blueprint('tracks', __name__, template_folder='templates', static_folder='static')

# For each blueprint can be separate folder with it's resources
# they can be easily get like this:
# with radios_page.open_resource('static/style.css') as f:
#     code = f.read()

# admin = Blueprint('admin', __name__, static_folder='static')
# url_for('admin.static', filename='style.css')


@tracks.route('/')
# @login_required
def tracks_list():
    tracks_data = Track.get_tracks(end_id=15)
    return render_template('tracks.html', tracks_data=tracks_data)
