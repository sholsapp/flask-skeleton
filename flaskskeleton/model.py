from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String


db = SQLAlchemy()


class Messages(db.Model):
  """A database table for messages."""
  __tablename__ = 'messages'
  id = db.Column(db.Integer, primary_key=True)
  message = db.Column(db.String(80))
  def __repr__(self):
    return 'Messages(%r)' % repr(self.message)
  def __init__(self, message):
    self.message = message


def make_conn_str():
  """Make an local database file on disk."""
  return 'sqlite:///flaskskeleton.db'
