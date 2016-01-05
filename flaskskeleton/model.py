from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from sqlalchemy import Column, Integer, String


db = SQLAlchemy()


class User(db.Model):
  """A user table for web application users.

  Web application users are users that can access routes protected by the
  :func:`~flask.ext.login.login_required` function.

  :param str username: The user's name.
  :param str password: The user's plain text password.
  :param str email: The user's email address.

  """
  __tablename__ = 'user'

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(8), unique=True, index=True)
  password = db.Column(db.String(128))
  email = db.Column(db.String(128), unique=True, index=True)

  def __init__(self, username, password, email):
    self.username = username
    self.password = self.encrypt_password(password)
    self.email = email

  @property
  def is_authenticated(self):
    """True if user is authenticated."""
    return True

  @property
  def is_anonymous(self):
    """True if user is anonymous."""
    return False

  @property
  def is_active(self):
    """True if user is active."""
    return True

  def get_id(self):
    """Get the user's primary key."""
    return unicode(self.id)

  def encrypt_password(self, password):
    """Encrypt a password.

    :param str password: The user's plain text password.
    :returns: The user's salted and encrypted password suitable for
      persisting to a database.
    :rtype: str

    """
    return sha256_crypt.encrypt(password)

  def  verify_password(self, password):
    """Check a password.

    :param str password: The user's plain text password.
    :returns: True if the user's password is correct.
    :rtype: bool

    """
    return sha256_crypt.verify(password, self.password)

  def __repr__(self):
    return 'User(username=%r)'.format(self.username)


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
