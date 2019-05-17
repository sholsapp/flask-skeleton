import logging
import os
import datetime

from authlib.flask.client import OAuth
from flask import Flask, render_template, jsonify, redirect, url_for, request, abort
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_restless import APIManager, ProcessingException
from flask_security import SQLAlchemyUserDatastore, Security, auth_token_required, current_user, login_required, login_user
from flask_security.utils import encrypt_password
from loginpass import create_flask_blueprint, Google
import authlib
import sqlalchemy

from flaskskeleton.api import api
from flaskskeleton.model import make_conn_str, db, User, Role, OAuth2Token


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


app = Flask(__name__)


def restless_api_auth_func(*args, **kw):
    """A request processor that ensures requests are authenticated.

    Flask-Restless endpoints are generated automatically and thus do not have a
    Flask route function that we can decorate with the
    :func:`flask.ext.security.auth_token_required` decorator. This function
    mimics the route function and satisfies the Flask-Restless request processor
    contract.

    """
    @auth_token_required
    def check_authentication():
        return
    rsp = check_authentication()
    # TODO(sholsapp): There are additional response codes that would result in
    # processing exceptions, this need to be addressed here.
    if rsp and rsp.status_code in [401]:
        raise ProcessingException(description='Not authenticated!', code=401)


def authlib_handle_authorize(remote, token, user_info):
    """Handle an OAuth2 authorization flow.

    This method is a OAuthlib construct, see documentation for more
    information.

    Handle an OAuth2 authorization flow by updating or creating a record for
    the authorization in our database.

    """

    log.info('Handling authorize for [%s] against [%s].', user_info.email, remote.name)

    if not current_user.is_authenticated:
        return redirect(url_for('security.login'))

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
        log.error('Failed to commit new or updated token...')
        db.session.rollback()

    return redirect(url_for('calendar'))


def authlib_fetch_token(name):
    """Fetch a token from the database.

    This method is a OAuthlib construct, see documentation for more
    information.

    Fetch a token from the database to refresh or initialize a new session for
    the signed in user.

    :param str name: The name of the remote to refresh or initialize the new
        session for.

    """

    log.info('Fetching token for [%s].', name)

    user_id = current_user.id

    item = OAuth2Token.query.filter_by(
        name=name, user_id=user_id,
    ).first()

    if item:
        return item.to_token()


def authlib_update_token(name, token):
    """Update a token.

    This method is a OAuthlib construct, see documentation for more
    information.

    Update a token that has expired for the the remote.

    :param str name: The name of the remote to update the token for.

    """

    log.info('Updating token for [%s].', name)

    item = OAuth2Token.query.filter_by(
        name=name, user_id=current_user.id
    ).first()

    if not item:
        item = OAuth2Token(name=name, user_id=current_user.id)

    # Do an in-place update from the token.
    item.from_token(token)

    db.session.add(item)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        log.error('Failed to commit updated token...')
        db.session.rollback()

    return item.to_token()


def init_webapp(test=False):
    """Initialize the web application.

    Initializes and configures the Flask web application. Call this method to
    make the web application and respective database engine usable.

    If initialized with `test=True` the application will use an in-memory
    SQLite database, and should be used for unit testing, but not much else.

    """

    # logging.getLogger('flask_cors').level = logging.DEBUG

    # Note, this url namespace also exists for the Flask-Restless extension and
    # is where CRUD interfaces live, so be careful not to collide with model
    # names here. We could change this, but it's nice to have API live in the
    # same url namespace.
    app.register_blueprint(api, url_prefix='/api')

    # Initialize Flask configuration
    if test:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = make_conn_str()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'abc123')
    app.config['SECURITY_TOKEN_MAX_AGE'] = 60
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Auth-Token'
    app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SALT', 'salt123')

    # Initialize Flask-CORS
    CORS(app, supports_credentials=True)
    # CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Initialize Flask-Bootstrap
    Bootstrap(app)

    # Initialize Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    Security(app, user_datastore)

    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID', 'abc123')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET', 'password')
    app.config['GOOGLE_CLIENT_KWARGS'] = dict(
        scope=' '.join([
            'openid',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/calendar.readonly',
        ])
    )

    # Initialize Authlib.
    oauth = OAuth()
    oauth.init_app(app, fetch_token=authlib_fetch_token, update_token=authlib_update_token)
    google_blueprint = create_flask_blueprint(Google, oauth, authlib_handle_authorize)
    app.register_blueprint(google_blueprint, url_prefix='/google')
    # Save the oauth object in the app so handlers can use it to build clients.
    app.oauth = oauth

    # Initialize Flask-SQLAlchemy
    db.app = app
    db.init_app(app)
    db.create_all()

    # Initialize Flask-Restless
    manager = APIManager(
        app,
        flask_sqlalchemy_db=db,
        preprocessors=dict(GET_MANY=[restless_api_auth_func]),
    )
    # manager.create_api(TableName methods=['GET', 'POST', 'OPTIONS'])
    return app


@app.route('/calendar')
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
        OAuth2Token.query.filter_by(user_id=user_id, name='google').one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('loginpass_google.login'))

    try:
        response = app.oauth.google.get(
            'calendar/v3/calendars/primary/events',
            params={'maxResults': 10, 'timeMin': '2017-01-01T12:00:00Z'},
        )
        if response.ok:
            return render_template('calendar.html', events=response.json()['items'])
    except authlib.oauth2.rfc6750.errors.InvalidTokenError:
        log.error('Request made with invalid token...')
        abort(500)
    except authlib.client.errors.MissingTokenError:
        log.error('Request made without a token...')
        abort(500)


@app.route('/')
def index():
    """A landing page.

    Nothing too interesting here.

    """
    return render_template('index.html', user=current_user)


@app.route('/register')
def register():
    """A registration page.

    Renders a simple registration page to create a new user.

    """
    return render_template('register.html')


@app.route('/signup', methods=['POST'])
def signup():
    """A signup endpoint.

    Look for "email" and "password" fields in form data or JSON payload to sign
    up a user.

    """

    email = None
    password = None

    # Support old-style form posts.
    if request.content_type == 'application/x-www-form-urlencoded':
        email = request.form.get('email')
        password = request.form.get('password')

    # Support new-style JSON posts.
    elif request.content_type == 'application/json':
        email = request.json.get('email')
        password = request.json.get('password')

    if not (email and password):
        abort(503)

    user = User(
        email=email,
        password=encrypt_password(password),
        active=True,
        confirmed_at=datetime.datetime.utcnow(),
    )

    db.session.add(user)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        log.error('Failed to commit new user...')
        db.session.rollback()

    # On sign up, also log the new user in before redirecting them to the landing
    # page.
    login_user(user)

    return redirect(url_for('index'))


@app.route('/protected')
@auth_token_required
def json_endpoint():
    """A protected API endpoint.

    Demonstrates how to expose a JWT authentication protected API endpoint to a
    upstream.

    """
    return jsonify({
        'username': current_user.email,
        'is_authenticated': current_user.is_authenticated,
    })
