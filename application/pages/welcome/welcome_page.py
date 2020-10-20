from flask import Blueprint, render_template, session
from application.db_models.radio_db import Radio
from flask import current_app as app
# from application.apis.radios.root import list_radios

welcome = Blueprint('welcome', __name__, template_folder='templates', static_folder='static')

@welcome.route('/')
def get_started():
    from config import APIConfig, config_class_to_dict
    session['api_keys'] = config_class_to_dict(APIConfig)
    print(session)
    return render_template('welcome_page.html')