import logging

from flask import Flask, render_template, jsonify
from flask.ext.bootstrap import Bootstrap
from flask.ext.restless import APIManager

from flaskskeleton.api import api
from flaskskeleton.model import make_conn_str, db, Messages


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


# Initialize Flask and register a blueprint
app = Flask(__name__)
# Note, this url namespace also exists for the Flask-Restless
# extension and is where CRUD interfaces live, so be careful not to
# collide with model names here. We could change this, but it's nice
# to have API live in the same url namespace.
app.register_blueprint(api, url_prefix='/api')

# Initialize Flask-Restless
manager = APIManager(app, flask_sqlalchemy_db=db)

# Initialize Flask-Bootstrap
Bootstrap(app)


def init_webapp():
  """Initialize the web application."""
  app.config['SQLALCHEMY_DATABASE_URI'] = make_conn_str()
  db.app = app
  db.init_app(app)
  db.create_all()
  manager.create_api(Messages, methods=['GET', 'POST'])
  return app


@app.route('/')
def index():
  log.debug('Someone accessed index.html!')
  return render_template('index.html', messages=Messages.query.all())


@app.route('/json')
def json_endpoint():
  return jsonify({'hello': 'world'})
