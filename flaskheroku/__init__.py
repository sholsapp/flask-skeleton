from flask import Flask, render_template, jsonify
from flask.ext.bootstrap import Bootstrap

from flaskheroku.api import api
from flaskheroku.model import make_conn_str, db


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')


Bootstrap(app)


def init_webapp():
  app.config['SQLALCHEMY_DATABASE_URI'] = make_conn_str()
  db.init_app(app)
  return app


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/json')
def json_endpoint():
  return jsonify({'hello': 'world'})
