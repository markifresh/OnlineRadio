from flask import Flask, _app_ctx_stack
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session
from application.apis.auth import oauth


# Globally accessible libraries
#db = SQLAlchemy()

def create_app(confConfClass):
    """Initialize the core application."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(confConfClass)

    # Initialize Plugins
    #db.init_app(app)
    from application.db_models import create_db
    db_session = create_db(confConfClass)
    app.session = scoped_session(db_session, scopefunc=_app_ctx_stack.__ident_func__)

    with app.app_context():
        # # Include our Routes
        # from . import routes
        #
        # # Register Blueprints
        # app.register_blueprint(auth.auth_bp)
        # app.register_blueprint(admin.admin_bp)
        from .pages.radios import radios_page
        from application.apis.auth import oauth

        app.register_blueprint(radios_page.radios)
        app.register_blueprint(oauth.oauth_api)

        from .db_models.radio_db import Radio
        print(Radio.all())
        # from .db_models import Radio
        # Radio.set_session(app.session)
        return app