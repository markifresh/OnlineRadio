from flask import Blueprint, render_template, session
from application.db_models.tracks_import import TracksImport
from flask import current_app as app
# from application.apis.radios.root import list_radios

imports = Blueprint('imports', __name__, template_folder='templates', static_folder='static')

# For each blueprint can be separate folder with it's resources
# they can be easily get like this:
# with radios_page.open_resource('static/style.css') as f:
#     code = f.read()

# admin = Blueprint('admin', __name__, static_folder='static')
# url_for('admin.static', filename='style.css')

@imports.route('/')
def imports_list():
    imports = TracksImport.get_imports(end_id=15)
    return render_template('imports.html', imports=imports)
