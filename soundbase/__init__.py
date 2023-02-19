import os

from flask import Flask, g
from soundbase import db as db_module

def create_app(test_config=None):
    # creating the application instance and setting default config
    app = Flask(__name__, instance_relative_config=True)

    with app.app_context():
        g.db=db.Database()
    # load config
    if test_config is None:
        # load from config.py file, if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load from passed config
        app.config.from_mapping(test_config)

    with app.app_context():
        @app.teardown_request
        def drop_db_connection(exception):
            if db_module.has_connection():
                g.db.close_connection()

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app


def register_blueprints(app):
    from . import auth
    app.register_blueprint(auth.bp, url_prefix='/')
    from . import views
    app.register_blueprint(views.bp, url_prefix='/')
    from . import views_artist
    app.register_blueprint(views_artist.bp, url_prefix='/admin')
    from . import views_user
    app.register_blueprint(views_user.bp, url_prefix='/admin')
    from . import views_track
    app.register_blueprint(views_track.bp, url_prefix='/admin')
    from . import views_release
    app.register_blueprint(views_release.bp, url_prefix='/admin')
    from . import views_rating
    app.register_blueprint(views_rating.bp, url_prefix='/admin')
    from . import views_soundbaseUser
    app.register_blueprint(views_soundbaseUser.bp, url_prefix='/')
    return app
