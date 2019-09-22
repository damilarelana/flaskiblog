import os
from flask import Flask
from . import (  # `.` means you are importing from the same directory i.e. same package
    db,
    auth,
    blog
)
from flask_session.__init__ import Session


def create_app(test_config=None):  # application factory
    # create and instantiate an instance of Flask
    # `instance_relative_config=True` signifies that the app instance configuration files are relative to the instance folder
    # `test_config` is a key:value map required to signify testing nuances
    app = Flask(__name__, instance_relative_config=True)  # create instance

    # initialize default configurations for the newly instantiated app
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),  # secure random phrase used to sign session cookies et al.
        DATABASE=os.path.join(app.instance_path, 'blogdatabase.sqlite')  # define path for database upon autogeneration of the db
    )

    # Set the session
    app.config['SESSION_TYPE'] = 'filesystem'
    sess = Session()
    sess.init_app(app)

    # allows for alternative source of default configuration e.g. loading configuration from `config.py` [in the instance folder]
    if test_config is None:
        # load the instance config, if it exists when not testing
        app.config.from_pyfile('config.py', silent=True) 
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists i.e. creates the instance folder [in case it does not exist]
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello (to show the app works) based on the url path `/hello`
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # initialize the database, by calling `init_app()` from `db.py` : after initiliazing the app configs
    db.init_app(app)

    # initialize the registered auth blueprints, by calling `init_blueprint` from `auth.py` : after initializing the app database
    auth.init_blueprint(app)

    # initialize the registered blog blueprints, by calling `init_blueprint` from `blog.py` : after initializing the app database
    blog.init_blueprint(app)

    return app  # return a properly configured instance of the app
