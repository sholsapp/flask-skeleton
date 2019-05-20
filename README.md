# flask-skeleton

A "hello world" style Flask web server application that applies good practices
learned over the years. This application is meant to be copied and pasted,
refactored, and specialized to suit your needs.

  1. [Flask](http://flask.pocoo.org/)
  2. [Gunicorn](http://gunicorn.org/)
  3. [Flask-Restless](https://flask-restless.readthedocs.org/en/latest/)
  4. [Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy/)
  5. [Flask-Bootstrap](http://pythonhosted.org/Flask-Bootstrap/)
  6. [Flask-Script](http://flask-script.readthedocs.org/en/latest/)
  7. [Authlib](https://docs.authlib.org/en/latest/index.html)

Out of the box, it comes with a simple OAuth2 integration against Google
Calendar API.  If you want to use this integration, you'll need to follow the
directions [here](https://developers.google.com/calendar/auth) to setup an
application on your Google API Console. Export the client/secret to
`GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`, respectively. If you don't want this
integration, deleting this code should be straight forward.

# Documentation

- [Development](./docs/developing.md)
- [Alembic](./docs/bootstrapping-alembic.md)

# Related Works

Also see:

  1. [sean-/flask-skeleton](https://github.com/sean-/flask-skeleton)
