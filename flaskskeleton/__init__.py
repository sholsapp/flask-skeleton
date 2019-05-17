import logging
import os
import datetime

from authlib.client import OAuth2Session
from authlib.flask.client import OAuth
from flask import Flask, render_template, jsonify, redirect, url_for, request, abort
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from flask_restless import APIManager, ProcessingException
from flask_security import SQLAlchemyUserDatastore, Security, auth_token_required, current_user
from flask_security.utils import encrypt_password
from loginpass import create_flask_blueprint, Google
from werkzeug.security import gen_salt
import sqlalchemy

from flaskskeleton.api import api
from flaskskeleton.model import make_conn_str, db, Employee, User, Role, OAuth2Token


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# Initialize Flask and register a blueprint
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


def handle_authorize(remote, token, user_info):

    # TODO(sholsapp): Need to keep a mapping between this OAuth user_info and
    # the current_user (Flask Security construct). Need to make sure that folks
    # are logged in by this point.  The user_info follows a standard at
    # http://openid.net/specs/openid-connect-core-1_0.html#StandardClaims.
    user_id = 0

    try:
        t = OAuth2Token.query.filter_by(user_id=user_id, name=remote.name).one()
        t.token_type = token['token_type']
        t.access_token = token['access_token']
        t.refresh_token = token['refresh_token']
        t.expires_at = token['expires_at']
    except sqlalchemy.orm.exc.NoResultFound:
        db.session.add(OAuth2Token(
            user_id=0,
            name=remote.name,
            token_type=token['token_type'],
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            expires_at=token['expires_at'],
        ))
    except sqlalchemy.orm.exc.MultipleResultsFound:
        abort(500)

    db.session.commit()

    return redirect(url_for('calendar'))


def fetch_token(name):
    item = OAuth2Token.query.filter_by(
	name=name, user_id=0,
    ).first()
    return item.to_token()


def init_webapp():
    """Initialize the web application."""

    # logging.getLogger('flask_cors').level = logging.DEBUG

    # Note, this url namespace also exists for the Flask-Restless extension and
    # is where CRUD interfaces live, so be careful not to collide with model
    # names here. We could change this, but it's nice to have API live in the
    # same url namespace.
    app.register_blueprint(api, url_prefix='/api')

    # Initialize Flask configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = make_conn_str()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'abc123')
    app.config['SECURITY_TOKEN_MAX_AGE'] = 60
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Auth-Token'
    app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SALT', gen_salt(64))

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
            'https://www.googleapis.com/auth/calendar',
        ])
    )
    oauth = OAuth()
    oauth.init_app(app, fetch_token=fetch_token)
    google_blueprint = create_flask_blueprint(Google, oauth, handle_authorize)
    app.register_blueprint(google_blueprint, url_prefix='/google')
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
    manager.create_api(Employee, methods=['GET', 'POST', 'OPTIONS'])
    return app


@app.route('/calendar')
def calendar():
    # FIXME: This needs to be set to the current user.
    user_id = 0
    token = OAuth2Token.query.filter_by(user_id=user_id, name='google').one()
    response = app.oauth.google.get(
        'calendar/v3/calendars/primary/events',
        params={'maxResults': 10, 'timeMin': '2017-01-01T12:00:00Z'},
    )
    if response.ok:
        return render_template('calendar.html', events=response.json()['items'])


@app.route('/')
def index():
    return render_template('index.html', employees=Employee.query.all())

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/signup', methods=['POST'])
def signup():

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

    # Consider using Flask-WTForms here and elsewhere to take care of proper
    # validation for a real production application.
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

    return redirect(url_for('index'))


@app.route('/protected')
@auth_token_required
def json_endpoint():
    return jsonify({
        'username': current_user.email,
        'is_authenticated': current_user.is_authenticated,
    })
