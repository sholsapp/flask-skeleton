from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from sqlalchemy import Column, Integer, String
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required


db = SQLAlchemy()


roles_users = db.Table('roles_users',
  db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
  db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


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
