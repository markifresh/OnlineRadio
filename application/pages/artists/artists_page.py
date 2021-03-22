from flask import Blueprint, render_template, session
from application.db_models.track_db import Track
from flask import current_app as app
# from application.apis.radios.root import list_radios

artists = Blueprint('artists', __name__, template_folder='templates', static_folder='static')

# For each blueprint can be separate folder with it's resources
# they can be easily get like this:
# with radios_page.open_resource('static/style.css') as f:
#     code = f.read()

# admin = Blueprint('admin', __name__, static_folder='static')
# url_for('admin.static', filename='style.css')

@artists.route('/')
def artists_list():
    artists = Track.get_artists(limit=15)
    return render_template('artists.html', artists=artists)
