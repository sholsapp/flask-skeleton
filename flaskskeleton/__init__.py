import logging

from flask import Flask, request, render_template, jsonify
from flask.ext.bootstrap import Bootstrap
from flask.ext.cors import CORS
from flask.ext.restless import APIManager, ProcessingException
from flask.ext.security import (
  RoleMixin,
  SQLAlchemyUserDatastore,
  Security,
  UserMixin,
  auth_token_required,
  current_user,
  login_required,
)
from werkzeug.security import gen_salt

from flaskskeleton.api import api
from flaskskeleton.model import make_conn_str, db, Employee, User, Role


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


def init_webapp():
  """Initialize the web application."""

  # Note, this url namespace also exists for the Flask-Restless
  # extension and is where CRUD interfaces live, so be careful not to
  # collide with model names here. We could change this, but it's nice
  # to have API live in the same url namespace.
  app.register_blueprint(api, url_prefix='/api')

  # Initialize Flask configuration
  app.config['SQLALCHEMY_DATABASE_URI'] = make_conn_str()
  app.config['SECRET_KEY'] = 'abc123'
  app.config['WTF_CSRF_ENABLED'] = False
  app.config['SECURITY_TOKEN_MAX_AGE'] = 60
  app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Auth-Token'

  # Initialize Flask-CORS
  CORS(app, supports_credentials=True)

  # Initialize Flask-Bootstrap
  Bootstrap(app)

  # Initialize Flask-Security
  user_datastore = SQLAlchemyUserDatastore(db, User, Role)
  security = Security(app, user_datastore)

  # Initialize Flask-SQLAlchemy
  db.app = app
  db.init_app(app)
  db.create_all()

  # Initialize Flask-Restless
  manager = APIManager(
    app,
    flask_sqlalchemy_db=db,
    preprocessors=dict(GET_MANY=[restless_api_auth_func]))
  manager.create_api(Employee, methods=['GET', 'POST', 'OPTIONS'])
  return app


@app.route('/')
def index():
  return render_template('index.html', employees=Employee.query.all())


@app.route('/protected')
@auth_token_required
def json_endpoint():
  return jsonify({'username': current_user.email,
                  'is_authenticated': current_user.is_authenticated})
