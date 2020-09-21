from flask import Blueprint, render_template
from application.db_models.radio_db import Radio

radios_page = Blueprint('radios', __name__,
                        template_folder='templates')

# For each blueprint can be separate folder with it's resources
# they can be easily get like this:
# with radios_page.open_resource('static/style.css') as f:
#     code = f.read()

# admin = Blueprint('admin', __name__, static_folder='static')
# url_for('admin.static', filename='style.css')

@radios_page.route('/radios')
def radios_list():
    Radio_model = Radio()
    radios_json = Radio_model.export_all_radios_data_to_json()
    return render_template('radios_list.html', radios=radios_json)