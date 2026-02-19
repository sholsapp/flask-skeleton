import importlib
import logging
import os
import sys
import uuid

import sqlalchemy
from authlib.integrations.flask_client import OAuth
from configobj import ConfigObj
from flask import Flask, jsonify, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    auth_required,
    current_user,
    login_user,
)
from werkzeug.middleware.proxy_fix import ProxyFix

from flaskskeleton.api import api
from flaskskeleton.model import OAuth2Token, Role, User, db

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


__all__ = ["app", "init_webapp"]


app = Flask(__name__)


@app.cli.command()
def version():
    _version = importlib.metadata.version("flask-skeleton")
    print(f"flask-skeleton v{_version}")


def authlib_token_update(name, token, refresh_token=None, access_token=None):

    item = None

    # Find the old token in the database
    if refresh_token:
        item = OAuth2Token.query.filter_by(name=name, refresh_token=refresh_token).first()
    elif access_token:
        item = OAuth2Token.query.filter_by(name=name, access_token=access_token).first()
    else:
        return

    # Do an in-place update from the token.
    item.from_token(token)

    db.session.add(item)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        log.error("Failed to commit updated token...")
        db.session.rollback()

    return item.to_token()


def authlib_fetch_token(name):
    """Fetch a token from the database.

    This method is a OAuthlib construct, see documentation for more
    information.

    Fetch a token from the database to refresh or initialize a new session for
    the signed in user.

    :param str name: The name of the remote to refresh or initialize the new
        session for.

    """

    log.info("Fetching token for [%s].", name)

    user_id = current_user.id

    item = OAuth2Token.query.filter_by(
        name=name,
        user_id=user_id,
    ).first()

    print(item)

    if item:
        return item.to_token()

    log.warning("Failed to fetch token for [%s].", name)


def init_webapp(config_path, test=False):
    """Initialize the web application.

    Initializes and configures the Flask web application. Call this method to
    make the web application and respective database engine usable.

    If initialized with `test=True` the application will use an in-memory
    SQLite database, and should be used for unit testing, but not much else.

    :param config_path: The path to the ConfigObj configuration file.
    :param test: True if should initialize the webapp for testing (use
        in-memory database).

    """

    if not test:
        try:
            config = ConfigObj(config_path, configspec=f"{config_path}spec")
        except OSError:
            print(f"Failed to load the configuration file at {config_path}.")
            sys.exit(1)

    # Make app work with proxies (like nginx) that set proxy headers.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # logging.getLogger('flask_cors').level = logging.DEBUG

    # Note, this url namespace also exists for the Flask-Restless extension and
    # is where CRUD interfaces live, so be careful not to collide with model
    # names here. We could change this, but it's nice to have API live in the
    # same url namespace.
    app.register_blueprint(api, url_prefix="/api")

    # Initialize Flask configuration
    if test:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = config["webapp"]["database_uri"]

    # FIXME: Port these over to configobj.
    app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID", "abc123")
    app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET", "password")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "abc123")
    app.config["SECURITY_TOKEN_MAX_AGE"] = 60
    app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = "Auth-Token"
    app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
    app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SALT", "salt123")
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_CONFIRMABLE"] = False
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False

    # This thing is a supreme PIA with API, and because we're using token based
    # authentication.
    app.config["WTF_CSRF_ENABLED"] = False

    # Initialize Flask-CORS
    CORS(app, supports_credentials=True)
    # CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Initialize Flask-Bootstrap
    Bootstrap(app)

    # Initialize Flask-Security
    app.user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, app.user_datastore)

    # Initialize Authlib.
    oauth = OAuth()
    oauth.init_app(app)
    app.oauth = oauth

    # Register Google directly
    app.google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        fetch_token=authlib_fetch_token,
        update_token=authlib_token_update,
        client_kwargs={
            'scope': ' '.join([
                    'openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                ]),
        },
        authorize_params={'access_type': 'offline', 'prompt': 'consent'} # for refresh_token
    )

    # Initialize Flask-SQLAlchemy
    db.app = app
    db.init_app(app)

    # NOTE: You don't want to use this if you're using alembic, since alembic
    # is now in charge of creating/upgrading/downgrading your database. If you
    # choose to not use alembic, you can add this line here.
    #
    # with app.app_context():
    #   db.create_all()

    return app


@app.route('/login/google')
def google_login():
    redirect_uri = url_for('auth', _external=True)
    return app.google.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    # 1. Get the token from Google
    token = app.google.authorize_access_token()
    user_info = token.get('userinfo')
    email = user_info['email']


    # 2. Check if user exists in the Flask-Security datastore
    user = app.user_datastore.find_user(email=email)
    # 3. If they don't exist, create an account for them
    if not user:
        # We generate a random uuid for fs_uniquifier as required by Flask-Security-Too
        user = app.user_datastore.create_user(
            email=email,
            password=None, # OAuth users might not have local passwords
            fs_uniquifier=uuid.uuid4().hex
        )
        db.session.commit()

    t = OAuth2Token.query.filter_by(
        user_id=user.id,
        name='google',
    ).first()
    if not t:
        t = OAuth2Token(
            user_id=user.id,
            name='google',
        )
        current_user.tokens.append(t)

    t.from_token(token)

    db.session.add(t)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        log.error("Failed to commit new or updated token...")
        db.session.rollback()

    # 4. Hand off to Flask-Security to establish the session
    login_user(user)

    return redirect(url_for('index'))


@app.route("/")
def index():
    """A landing page."""
    return render_template("index.html", user=current_user)


@app.route("/protected")
@auth_required('token', 'session')
def json_endpoint():
    """A protected API endpoint."""
    return jsonify(
        {
            "username": current_user.email,
            "is_authenticated": current_user.is_authenticated,
        }
    )

@app.route("/health")
def health():
    return jsonify(
        {
            "version": importlib.metadata.version("flask-skeleton"),
        }
    )
