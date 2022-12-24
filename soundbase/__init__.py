import os
from flask import Flask


def create_app(test_config=None):
    # creating the application instance and setting default config
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # SECRET_KEY set to 'dev' for testing purposes
        SECRET_KEY='dev',
        # set path to be relative to the instance directory
        DATABASE=os.path.join(app.instance_path, 'soundbase.sqlite3')
    )

    # load config
    if test_config is None:
        # load from config.py file, if it exists
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load from passed config
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # display 'Hello World!'
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp,url_prefix='/')
    from . import views
    app.register_blueprint(views.bp,url_prefix='/')

    return app

