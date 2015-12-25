from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String


db = SQLAlchemy()


class Employee(db.Model):
  """A database table for employees."""
  __tablename__ = 'employee'
  id = db.Column(db.Integer, primary_key=True)
  first = db.Column(db.String(64))
  last = db.Column(db.String(64))
  position = db.Column(db.String(64))
  salary = db.Column(db.Integer)
  def __repr__(self):
    return 'Employee(%r, %r, %r)' % repr(self.id, self.first, self.last)
  def __init__(self, first, last, position, salary):
    self.first = first
    self.last = last
    self.position = position
    self.salary = salary


def make_conn_str():
  """Make an local database file on disk."""
  return 'sqlite:///flaskskeleton.db'
