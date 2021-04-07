from flask import Blueprint, render_template, session
from application.db_models.radio import Radio
from flask import current_app as app
# from application.apis.radios.root import list_radios

user_settings = Blueprint('user_settings', __name__, template_folder='templates', static_folder='static')

@user_settings.route('/')
def show_settings():
    # from config import APIConfig, config_class_to_dict
    # session['api_keys'] = config_class_to_dict(APIConfig)
    # print(session)
    return render_template('user_settings_page.html')