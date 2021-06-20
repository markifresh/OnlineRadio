from flask import Flask, _app_ctx_stack
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session
from flask_restx import Api
from flask_login import LoginManager
from flask_restx import fields
from config import DevConfig, ProdConfig, import_date_format, import_datetime_format
from datetime import date, datetime

# import werkzeug
# werkzeug.cached_property = werkzeug.utils.cached_property

# from flask_restplus import Api

# Globally accessible libraries
#db = SQLAlchemy()
login_manager = LoginManager()

def create_app(confConfClass):
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(confConfClass)

    api = Api(app,
              version='1.0',
              title='OnlineRadio API',
              description='API for online Radio',
              prefix='/api',
              doc='/api/docs/'
              )
    #
    # app.config.SWAGGER_UI_DOC_EXPANSION = 'list'


    # Initialize Plugins
    #db.init_app(app)
    from application.db_models import create_db
    db_session = create_db(confConfClass)
    app.db_session = scoped_session(db_session, scopefunc=_app_ctx_stack.__ident_func__)

    login_manager.init_app(app)

    with app.app_context():
        # # Include our Routes
        # from . import routes
        #
        # # Register Blueprints
        # app.register_blueprint(auth.auth_bp)
        # app.register_blueprint(admin.admin_bp)

        # from .apis.api_radios import radios_api
        # from .apis.tracks_api import tracks_api
        # # app.register_blueprint(radios_api, url_prefix='/api/radios')
        # app.register_blueprint(tracks_api)

        from application.extenders import jinja_extra
        app.register_blueprint(jinja_extra.jinja_extra)


        from .pages.welcome import welcome_page
        app.register_blueprint(welcome_page.welcome, url_prefix='/')

        from .pages.user_settings import user_settings_page
        app.register_blueprint(user_settings_page.user_settings, url_prefix='/settings')

        from application.pages.auth.auth_page import auth_page
        app.register_blueprint(auth_page, url_prefix='/auth')

        from .pages.radios import radios_page
        app.register_blueprint(radios_page.radios, url_prefix='/radios')

        from .pages.oauth_page import oauth
        app.register_blueprint(oauth, url_prefix='/oauth')
        
        from application.pages.statistics.statistics_page import statistics
        app.register_blueprint(statistics, url_prefix='/statistics')

        from application.pages.tracks.tracks_page import tracks
        app.register_blueprint(tracks, url_prefix='/tracks')

        from application.pages.artists.artists_page import artists
        app.register_blueprint(artists, url_prefix='/artists')

        from application.pages.tracks_imports.imports_page import imports
        app.register_blueprint(imports, url_prefix='/imports')

        from application.pages.tracks_exports.exports_page import exports
        app.register_blueprint(exports, url_prefix='/exports')


        # tracks = api.model('tracks', {
        #     'artist': fields.String(required=True, description='title of a track'),
        #     'title': fields.String(required=True, description='artist of a track'),
        # })

        from application.schema_models.users_schemas import users_schemas
        api.add_namespace(users_schemas)

        from application.schema_models.tracks_schemas import tracks_schemas
        api.add_namespace(tracks_schemas)

        from application.schema_models.dbimports_schemas import di_schemas
        api.add_namespace(di_schemas)

        from application.schema_models.radios_schemas import radios_schemas
        api.add_namespace(radios_schemas)

        from application.schema_models.exports_schemas import se_schemas
        api.add_namespace(se_schemas)

        from application.schema_models.tracks_schemas import tracks_schemas
        api.add_namespace(tracks_schemas)

        ### APIs INIT ###
        from application.apis.users_api import users_api
        api.add_namespace(users_api, '/users')

        from application.apis.radios_api import radios_api
        api.add_namespace(radios_api, '/radios')

        from application.apis.tracks_api import tracks_api
        api.add_namespace(tracks_api, '/tracks')

        from application.apis.dbimports_api import dbimports_api
        api.add_namespace(dbimports_api, '/imports')

        from application.apis.spotifyexports_api import spotifyexports_api
        api.add_namespace(spotifyexports_api, '/exports')

        from application.apis.radio_tracks_api import radio_tracks_api
        api.add_namespace(radio_tracks_api, '/radio_tracks')

        from application.apis.radio_imports import radio_imports_api
        api.add_namespace(radio_imports_api, '/radio_imports')

        from application.apis.radio_exports import radio_exports_api
        api.add_namespace(radio_exports_api, '/radio_exports')

        # from application.apis import Test2
        # app.register_blueprint(Test2.radios_api2)

        # from application.apis.Test import api as meals_api
        # api.add_namespace(meals_api, '/test')


        # api.init_app(app)
        # from .db_models import Radio
        # Radio.set_session(app.session)

        # app = Api(app=app,
        #           version="1.0",
        #           title="Name Recorder",
        #           description="Manage names of various users of the application")
        return app

def create_dbs():
    from application.db_models.radio import Radio
    Radio.create_tables()
    # Radio.update_radios_list

def convert_to_date(date_input):
    full_date = None
    if isinstance(date_input, str) and '-' in date_input:
        date_input = date_input.split(' ')
        if len(date_input) == 2:
            date_date, date_time = date_input
            if ':' in date_date:
                date_time, date_date = date_date, date_time
            full_date = datetime.strptime(date_date + ' ' + date_time, import_datetime_format)
        else:
            full_date = datetime.strptime(date_input[0], import_date_format)

    elif isinstance(date_input, datetime):
        full_date = date_input

    elif isinstance(date_input, date):
        full_date = datetime(date_input.year, date_input.month, date_input.day)

    if not full_date:
        raise Exception(f'Date "{date_input}" does not match supported formats'
                        f' ({import_date_format}, {import_datetime_format})')

    return full_date

def get_data_range(start_date, end_date):
    start_date = convert_to_date(start_date)
    end_date = convert_to_date(end_date)

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    return start_date, end_date