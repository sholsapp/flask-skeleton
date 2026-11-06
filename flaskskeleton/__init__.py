import importlib
import logging
import os
import sys
import uuid

import sqlalchemy
from authlib.integrations.flask_client import OAuth
from configobj import ConfigObj
from flask import Flask, Response, abort, jsonify, redirect, render_template, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    auth_required,
    current_user,
    login_user,
    logout_user,
)
from werkzeug.middleware.proxy_fix import ProxyFix

from flaskskeleton.model import OAuth2Token, Pokemon, Role, User, db

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


__all__ = ["app", "init_webapp"]


app = Flask(__name__)


@app.cli.command()
def version() -> None:
    """Print the current version of flask-skeleton.

    :return: None

    """
    _version = importlib.metadata.version("flask-skeleton")
    print(f"flask-skeleton v{_version}")


def authlib_token_update(
    name: str, token: dict, refresh_token: str = None, access_token: str = None
) -> dict | None:
    """Update an OAuth2 token in the database.

    This method is an Authlib construct, see Authlib documentation for more
    information.

    :param name: The name of the remote provider.
    :param token: The new token data.
    :param refresh_token: The refresh token to match.
    :param access_token: The access token to match.
    :return: The updated token as a dict, or None if not found.
    :raises sqlalchemy.exc.IntegrityError: If database commit fails.

    """

    item = None

    # Find the old token in the database
    if refresh_token:
        item = OAuth2Token.query.filter_by(
            name=name, refresh_token=refresh_token
        ).first()
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


def authlib_fetch_token(name: str) -> dict | None:
    """Fetch a token from the database.

    This method is an Authlib construct, see Authlib documentation for more
    information.

    Fetch a token from the database to refresh or initialize a new session for
    the signe-in user.

    :param name: The name of the remote to refresh or initialize the new
        session for.
    :return: The token as a dict, or None if not found.

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


class SecureModelView(ModelView):
    """A Flask-Admin ModelView that requires authentication.

    Only authenticated users (via token or session) can access admin model
    views. Unauthenticated users are redirected to the login page.
    """

    def is_accessible(self) -> bool:
        """Check if the current user is authenticated.

        :return: True if the user is authenticated, False otherwise.
        """
        return current_user.is_active and current_user.is_authenticated

    def inaccessible_callback(self, name: str, **kwargs) -> Response:
        """Redirect unauthenticated users to the login page.

        :param name: The name of the view being accessed.
        :return: A redirect response to the login page.
        """
        return redirect(url_for("login", next=url_for(name, **kwargs)))


class SecureAdminIndexView(AdminIndexView):
    """A Flask-Admin index view that requires authentication.

    Only authenticated users can access the admin index page.
    Unauthenticated users are redirected to the login page.
    """

    @expose("/")
    def index(self) -> str:
        """Render the admin index page if authenticated.

        :return: Rendered HTML for the admin index page, or a redirect
            to the login page.
        """
        if not current_user.is_active or not current_user.is_authenticated:
            return redirect(url_for("login", next=url_for("admin.index")))
        return super().index()


def init_webapp(config_path: str, test: bool = False) -> Flask:
    """Initialize the web application.

    Initializes and configures the Flask web application. Call this method to
    make the web application and respective database engine usable.

    If initialized with `test=True` the application will use an in-memory
    SQLite database, and should be used for unit testing, but not much else.

    :param config_path: The path to the ConfigObj configuration file.
    :param test: True if should initialize the webapp for testing (use
        in-memory database).
    :return: The initialized Flask app instance.
    :raises OSError: If the configuration file cannot be loaded.

    """

    if not test:
        try:
            config = ConfigObj(config_path, configspec=f"{config_path}spec")
        except OSError:
            print(f"Failed to load the configuration file at {config_path}.")
            sys.exit(1)

    # Make app work with proxies (like nginx) that set proxy headers.
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Initialize Flask configuration
    #
    # FIXME: Port to configuration
    if test:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = config["webapp"]["database_uri"]
    app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID", "abc123")
    app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get(
        "GOOGLE_CLIENT_SECRET", "password"
    )
    app.config["OKTA_CLIENT_ID"] = os.environ.get("OKTA_CLIENT_ID", "abc123")
    app.config["OKTA_CLIENT_SECRET"] = os.environ.get("OKTA_CLIENT_SECRET", "password")
    app.config["OKTA_BASE_URL"] = os.environ.get(
        "OKTA_BASE_URL", "https://your-okta-domain.okta.com"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "abc123")
    app.config["SECURITY_TOKEN_MAX_AGE"] = 60
    app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = "Auth-Token"
    app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
    app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SALT", "salt123")
    app.config["SECURITY_REGISTERABLE"] = True
    app.config["SECURITY_CONFIRMABLE"] = False
    app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
    app.config["SECURITY_LOGIN_URL"] = "/login"
    app.config["SECURITY_LOGOUT_URL"] = "/logout"
    app.config["WTF_CSRF_ENABLED"] = False  # Doesn't play nice with token-based auth

    # Initialize Flask-SQLAlchemy
    db.init_app(app)

    # Only create the database during testing. In production, use alembic to
    # manage the database.
    if test:
        with app.app_context():
            db.create_all()

    # Initialize Flask-CORS
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Initialize Flask-Bootstrap
    Bootstrap(app)

    # Initialize Flask-Security
    app.user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, app.user_datastore)

    # Initialize Authlib.
    oauth = OAuth()
    oauth.init_app(app)
    app.oauth = oauth

    # Register Google identity provider
    app.google = oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        fetch_token=authlib_fetch_token,
        update_token=authlib_token_update,
        client_kwargs={
            "scope": " ".join(
                [
                    "openid",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile",
                ]
            ),
        },
        authorize_params={
            "access_type": "offline",
            "prompt": "consent",
        },  # for refresh_token
    )

    # Register Okta identity provider
    app.okta = oauth.register(
        name="okta",
        client_id=app.config["OKTA_CLIENT_ID"],
        client_secret=app.config["OKTA_CLIENT_SECRET"],
        server_metadata_url=f"{app.config['OKTA_BASE_URL']}/.well-known/openid-configuration",
        fetch_token=authlib_fetch_token,
        update_token=authlib_token_update,
        client_kwargs={
            "scope": " ".join(
                [
                    "openid",
                    "email",
                    "profile",
                    "offline_access",
                ]
            ),
        },  # for refresh_token
    )

    # Supported OAuth providers for the unified /auth route
    app.supported_providers = {"google", "okta"}

    # Initialize Flask-Admin with authentication-required views
    admin = Admin(app, name="Admin", index_view=SecureAdminIndexView())
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Role, db.session))
    admin.add_view(SecureModelView(Pokemon, db.session))

    return app


@app.route("/_auth/login/google")
def google_login():
    """
    Redirect the user to Google OAuth login.

    :return: A redirect response to Google OAuth.
    """
    redirect_uri = url_for(
        "auth_oidc_callback",
        provider="google",
        _external=True,
    )
    return app.google.authorize_redirect(redirect_uri)


@app.route("/_auth/login/okta")
def okta_login():
    """
    Redirect the user to Okta OAuth login.

    :return: A redirect response to Okta OAuth.
    """
    redirect_uri = url_for(
        "auth_oidc_callback",
        provider="okta",
        _external=True,
    )
    return app.okta.authorize_redirect(redirect_uri)


@app.route("/_auth/oidc/callback/<provider>")
def auth_oidc_callback(provider):
    """
    Handle OAuth callback for any supported provider, create user if needed,
    and log in.

    The provider is determined by the ``provider`` route parameter, which must
    be one of the supported providers (e.g. ``google``, ``okta``).

    :param provider: The name of the OAuth provider.
    :return: A redirect response to the index page.
    :raises werkzeug.exceptions.BadRequest: If the provider is unsupported.
    :raises sqlalchemy.exc.IntegrityError: If database commit fails.
    """
    if provider not in app.supported_providers:
        abort(400, description=f"Unsupported provider: {provider}")

    oauth_client = getattr(app.oauth, provider)
    token = oauth_client.authorize_access_token()

    user_info = token.get("userinfo")
    email = user_info.get("email")

    user = app.user_datastore.find_user(email=email)
    if not user:
        user = app.user_datastore.create_user(
            email=email,
            password=None,  # OAuth users might not have local passwords
            fs_uniquifier=uuid.uuid4().hex,
            active=True,
        )
        db.session.commit()

    login_user(user)

    t = OAuth2Token.query.filter_by(
        user_id=user.id,
        name=provider,
    ).first()
    if not t:
        t = OAuth2Token(
            user_id=user.id,
            name=provider,
        )
        current_user.tokens.append(t)

    t.from_token(token)

    db.session.add(t)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        log.error("Failed to commit new or updated token...")
        db.session.rollback()

    return redirect(url_for("index"))


@app.route("/login")
def login():
    """
    Render the login page.

    :return: Rendered HTML for the login page.
    """
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out the current user and destroy any associated OAuth2 tokens.

    Deletes all OAuth2 tokens for the current user from the database, then
    logs the user out and redirects to the index page.

    :return: A redirect response to the index page.
    """
    if current_user.is_authenticated:
        OAuth2Token.query.filter_by(user_id=current_user.id).delete()
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            log.error("Failed to delete tokens for user [%s].", current_user.email)
            db.session.rollback()

        logout_user()

    return redirect(url_for("index"))


@app.route("/")
def index():
    """
    Render the landing page.

    :return: Rendered HTML for the landing page.
    """
    return render_template("index.html", user=current_user)


@app.route("/protected")
@auth_required("token", "session")
def protected():
    """Example protected endpoint.

    :return: JSON response with user info.
    """
    return jsonify(
        {
            "username": current_user.email,
            "is_authenticated": current_user.is_authenticated,
        }
    )
