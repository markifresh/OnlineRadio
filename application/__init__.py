
from flask import Flask, _app_ctx_stack
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session
from application.db_models.extenders_for_db_models import db_session
from application.blueprints import radios_page
from application.apis.auth import oauth


# Globally accessible libraries
#db = SQLAlchemy()

def create_app(confConfClass):
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(confConfClass)

    # Initialize Plugins
    #db.init_app(app)
    app.session = scoped_session(db_session, scopefunc=_app_ctx_stack.__ident_func__)
    with app.app_context():
        # # Include our Routes
        # from . import routes
        #
        # # Register Blueprints
        # app.register_blueprint(auth.auth_bp)
        # app.register_blueprint(admin.admin_bp)
        app.register_blueprint(radios_page.radios_page)
        app.register_blueprint(oauth.oauth_api)

        return app