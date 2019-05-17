from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')),
)


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
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class OAuth2Token(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), primary_key=True)

    token_type = db.Column(db.String(20))
    access_token = db.Column(db.String(48), nullable=False)
    refresh_token = db.Column(db.String(48))
    expires_at = db.Column(db.Integer, default=0)

    def __init__(self, user_id, name, token_type, access_token, refresh_token, expires_at):
        self.user_id = user_id
        self.name = name
        self.token_type = token_type
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )

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
