import os

from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta

db = SQLAlchemy()

# This is a work around for mypy until SQLAlchemy supports type stubs.
BaseModel: DefaultMeta = db.Model


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id")),
)


class Role(BaseModel, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


# XXX: Consider adjusting this model to follow the standard discussed in
# http://openid.net/specs/openid-connect-core-1_0.html#StandardClaims. This is
# also the standard that the Authlib/Loginpass libraries use.
class User(BaseModel, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))
    tokens = db.relationship("OAuth2Token", back_populates="user")


class OAuth2Token(BaseModel):
    __tablename__ = "oauth2token"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name = db.Column(db.String(20), primary_key=True)
    token_type = db.Column(db.String(20))
    access_token = db.Column(db.String(48), nullable=False)
    refresh_token = db.Column(db.String(48))
    expires_at = db.Column(db.Integer, default=0)
    #: ORM link to user table.
    user = db.relationship("User", back_populates="tokens")

    def __init__(self, user_id, name, token_type=None, access_token=None, refresh_token=None, expires_at=None):
        self.user_id = user_id
        self.name = name
        self.token_type = token_type
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = expires_at

    def from_token(self, token):
        self.token_type = token["token_type"]
        self.access_token = token["access_token"]
        self.refresh_token = token["refresh_token"]
        self.expires_at = token["expires_at"]

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
        )


def make_conn_str():
    """Make an local database file on disk."""
    return "sqlite:///{cwd}/database.db".format(cwd=os.path.abspath(os.getcwd()))
