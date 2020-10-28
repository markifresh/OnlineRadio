from flask import Blueprint, render_template, session
from application.db_models.radio_db import Radio
from flask import current_app as app
# from application.apis.radios.root import list_radios

radios = Blueprint('radios', __name__, template_folder='templates', static_folder='static')

# For each blueprint can be separate folder with it's resources
# they can be easily get like this:
# with radios_page.open_resource('static/style.css') as f:
#     code = f.read()

# admin = Blueprint('admin', __name__, static_folder='static')
# url_for('admin.static', filename='style.css')

@radios.route('/')
def radios_list():
    radios_data = Radio.get_data_for_radios_page()
    return render_template('radios_list.html', radios=radios_data)