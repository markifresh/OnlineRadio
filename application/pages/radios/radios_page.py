from flask import Blueprint, render_template, session
from application.db_models.user import User
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
    radios_data = User.get_user_radio_page_data(session['ms_user']['id'])
    return render_template('radios_list.html', radios=radios_data)
