from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String


db = SQLAlchemy()


class Messages(db.Model):
  id = Column(Integer, primary_key=True)
  message = Column(String(80))
  def __repr__(self):
    return 'Messages(%r)' % repr(self.message)
  def __init__(self, message):
    self.message = message


def make_conn_str():
  """Make an in memory database for now."""
  return 'sqlite://'
