# flask-skeleton

A "hello world" style Flask web server application that applies good practices
learned over the years. This application is meant to be copied and pasted,
refactored, and specialized to suit your needs.

- [APScheduler](https://apscheduler.readthedocs.io/en/latest/index.html)
- [Authlib](https://docs.authlib.org/en/latest/index.html)
- [Flask-Bootstrap](http://pythonhosted.org/Flask-Bootstrap/)
- [Flask-Restless](https://flask-restless.readthedocs.org/en/latest/)
- [Flask-SQLAlchemy](https://pythonhosted.org/Flask-SQLAlchemy/)
- [Flask-Script](http://flask-script.readthedocs.org/en/latest/)
- [Flask-Security](https://pythonhosted.org/Flask-Security/)
- [Flask](http://flask.pocoo.org/)
- [Gunicorn](http://gunicorn.org/)

Out of the box, it comes with a simple OAuth2 integration against Google
Calendar API.  If you want to use this integration, you'll need to follow the
directions [here](https://developers.google.com/calendar/auth) to setup an
application on your Google API Console. Export the client/secret to
`GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`, respectively. If you don't want this
integration, deleting this code should be straight forward.

# documentation

- [Developing](./docs/developing.md)
- [Bootstrapping Alembic](./docs/bootstrapping-alembic.md)
- Environment (WIP)

# build

Use Docker to build and run the server locally.

```bash
docker build -t sholsapp/flask-skeleton .
docker run --publish 5000:5000 sholsapp/flask-skeleton
```

# related works

Also see:

  1. [sean-/flask-skeleton](https://github.com/sean-/flask-skeleton)
  2. [graup/flask-restless-security](https://github.com/graup/flask-restless-security)
  3. [imwilsonxu/fbone](https://github.com/imwilsonxu/fbone)
  4. [xen/flask-project-template](https://github.com/xen/flask-project-template)
  5. [jelmerdejong/flask-app-blueprint](https://github.com/jelmerdejong/flask-app-blueprint)
