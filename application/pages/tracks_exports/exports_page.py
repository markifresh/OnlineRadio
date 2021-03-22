from flask import Blueprint, render_template, session
from application.db_models.spotifyexport_db import SpotifyExport
from flask import current_app as app
# from application.apis.radios.root import list_radios

exports = Blueprint('exports', __name__, template_folder='templates', static_folder='static')

# For each blueprint can be separate folder with it's resources
# they can be easily get like this:
# with radios_page.open_resource('static/style.css') as f:
#     code = f.read()

# admin = Blueprint('admin', __name__, static_folder='static')
# url_for('admin.static', filename='style.css')

@exports.route('/')
def exports_list():
    exports = SpotifyExport.get_exports(end_id=15)
    return render_template('exports.html', exports=exports)
