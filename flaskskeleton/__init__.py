import logging
import os
import sys

import authlib
import pkg_resources
import sqlalchemy
from authlib.integrations.flask_client import OAuth
from configobj import ConfigObj
from flask import Flask, abort, jsonify, redirect, render_template, url_for
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    auth_token_required,
    current_user,
    login_required,
)
from loginpass import Google, create_flask_blueprint
from werkzeug.middleware.proxy_fix import ProxyFix

from flaskskeleton.api import api
from flaskskeleton.model import OAuth2Token, Role, User, db

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


app = Flask(__name__)


@app.cli.command()
def version():
    _version = pkg_resources.get_distribution("flask-skeleton").version
    print(f"flask-skeleton v{_version}")


def authlib_handle_authorize(remote, token, user_info):
    """Handle an OAuth2 authorization flow.

    This method is a OAuthlib construct, see documentation for more
    information.

    Handle an OAuth2 authorization flow by updating or creating a record for
    the authorization in our database.

    """

    log.info("Handling authorize for [%s] against [%s].", user_info.email, remote.name)

    if not current_user.is_authenticated:
        return redirect(url_for("security.login"))

    user_id = current_user.id

    t = OAuth2Token.query.filter_by(
        user_id=user_id,
        name=remote.name,
    ).first()
    if not t:
        t = OAuth2Token(
            user_id=user_id,
            name=remote.name,
        )
        current_user.tokens.append(t)

    t.from_token(token)

    db.session.add(t)

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        log.error("Failed to commit new or updated token...")
        db.session.rollback()

    return redirect(url_for("calendar"))


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

    if item:
        return item.to_token()

    log.warning("Failed to fetch token for [%s].", name)


def authlib_update_token(name, token):
    """Update a token.

    This method is a OAuthlib construct, see documentation for more
    information.

    Update a token that has expired for the the remote.

    :param str name: The name of the remote to update the token for.

    """

    log.info("Updating token for [%s].", name)

    item = OAuth2Token.query.filter_by(name=name, user_id=current_user.id).first()

    if not item:
        item = OAuth2Token(name=name, user_id=current_user.id)

    # Do an in-place update from the token.
    item.from_token(token)

    db.session.add(item)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        log.error("Failed to commit updated token...")
        db.session.rollback()

    return item.to_token()


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
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID", "abc123")
    app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET", "password")
    app.config["GOOGLE_REFRESH_TOKEN_URL"] = "https://www.googleapis.com/oauth2/v4/token"
    app.config["GOOGLE_CLIENT_KWARGS"] = dict(
        scope=" ".join(
            [
                "openid",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/calendar.readonly",
            ]
        )
    )
    app.config["GOOGLE_AUTHORIZE_PARAMS"] = {"access_type": "offline"}

    # Initialize Authlib.
    oauth = OAuth()
    oauth.init_app(app, fetch_token=authlib_fetch_token, update_token=authlib_update_token)
    google_blueprint = create_flask_blueprint([Google], oauth, authlib_handle_authorize)
    app.register_blueprint(google_blueprint, url_prefix="/google")
    # Save the oauth object in the app so handlers can use it to build clients.
    app.oauth = oauth

    # Initialize Flask-SQLAlchemy
    db.app = app
    db.init_app(app)

    # NOTE: You don't want to use this if you're using alembic, since alembic
    # is now in charge of creating/upgrading/downgrading your database. If you
    # choose to not use alembic, you can add this line here.
    # db.create_all()

    return app


@app.route("/calendar")
@login_required
def calendar():
    """A interesting integration.

    Use an OAuth client to do somethign interesting.

    Demonstrates how to use the OAuthlib client that we initiated earlier and
    saved in the app object.

    """

    user_id = current_user.id

    # Just ensure that the user has a token, otherwise redirect them to the
    # OAuth login/authorization flow.
    try:
        OAuth2Token.query.filter_by(user_id=user_id, name="google").one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for("loginpass.login", name="google"))

    try:
        response = app.oauth.google.get(
            "calendar/v3/calendars/primary/events",
            params={"maxResults": 10, "timeMin": "2017-01-01T12:00:00Z"},
        )
        if response.ok:
            return render_template("calendar.html", events=response.json()["items"])
    except authlib.oauth2.rfc6750.errors.InvalidTokenError:
        log.error("Request made with invalid token...")
        abort(500)
    except authlib.client.errors.MissingTokenError:
        log.error("Request made without a token...")
        abort(500)


@app.route("/")
def index():
    """A landing page.

    Nothing too interesting here.

    """
    return render_template("index.html", user=current_user)


@app.route("/protected")
@auth_token_required
def json_endpoint():
    """A protected API endpoint.

    Demonstrates how to expose a JWT authentication protected API endpoint to a
    upstream.

    """
    return jsonify(
        {
            "username": current_user.email,
            "is_authenticated": current_user.is_authenticated,
        }
    )


@app.route("/admin")
def admin():
    return jsonify(
        {
            "version": pkg_resources.get_distribution("flask-skeleton").version,
        }
    )
