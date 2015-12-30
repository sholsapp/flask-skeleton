import logging

from flask import Flask, request, render_template, jsonify, Response
from flask.ext.bootstrap import Bootstrap
from flask.ext.cors import CORS
from flask.ext.login import LoginManager, login_required, login_user, logout_user
from flask.ext.restless import APIManager

from flaskskeleton.api import api
from flaskskeleton.model import make_conn_str, db, Employee, User


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# Initialize Flask and register a blueprint
app = Flask(__name__)
CORS(app)

# Note, this url namespace also exists for the Flask-Restless
# extension and is where CRUD interfaces live, so be careful not to
# collide with model names here. We could change this, but it's nice
# to have API live in the same url namespace.
app.register_blueprint(api, url_prefix='/api')

# Initialize Flask-Restless
manager = APIManager(app, flask_sqlalchemy_db=db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Flask-Bootstrap
Bootstrap(app)


@login_manager.user_loader
def load_user(id):
  return User.query.get(int(id))


def init_webapp():
  """Initialize the web application."""
  app.config['SQLALCHEMY_DATABASE_URI'] = make_conn_str()
  app.config['SECRET_KEY'] = 'abc123'
  db.app = app
  db.init_app(app)
  db.create_all()
  # TODO(sholsapp): Build a request process that requires authentication for
  # Flask-Restless API, otherwise these will be accessible by everyone.
  manager.create_api(Employee, methods=['GET', 'POST', 'OPTIONS'])
  return app


@app.route('/')
def index():
  log.debug('Someone accessed index.html!')
  return render_template('index.html', employees=Employee.query.all())


@app.route('/login')
def login():
  # TODO(sholsapp): Validate these values taken from the user before using
  # them for anything internally.
  username = request.args.get('username')
  password = request.args.get('password')
  remember_me = request.args.get('remember_me')
  if not username or not password:
    return Response(status=400)
  user = User.query.filter_by(username=username).first()
  if user:
    if user.verify_password(password):
      login_user(user, remember=remember_me)
      return Response(status=200)
    return Response(status=401)
  else:
    return Response(status=403)


@app.route('/logout')
def logout():
  logout_user()
  return Response(status=200)


@app.route('/protected')
@login_required
def json_endpoint():
  return jsonify({'hello': 'world'})
