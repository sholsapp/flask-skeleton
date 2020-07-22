# Flask Skeleton

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

# Documentation

- [Developing](./docs/developing.md)
- [Bootstrapping Alembic](./docs/bootstrapping-alembic.md)
- [Configuration](./docs/configuration.md)

# Quickstart

Use Docker to build and run the webapp locally.

```bash
docker build -t sholsapp/flask-skeleton:0.1 .
docker run --publish 5000:5000 --detach sholsapp/flask-skeleton:0.1
# You'll need to log in to the container and initialize the database using
# alembic unless you're using a remote database.
# $ alembic upgrade head
curl http://0.0.0.0:5000/
```

# Packaging

Use Docker to build a deployable .deb package, and create a container to copy
the .deb to the local host's current directory.

```
docker build -f Dockerfile --target builder -t sholsapp/flask-skeleton-builder .
docker create --cidfile .tmp-docker-container-id sholsapp/flask-skeleton-builder
xargs -I {} docker cp -a "{}:/build/flask-skeleton_0.1-1_amd64.deb" . < .tmp-docker-container-id
xargs -I {} docker rm -f "{}" < .tmp-docker-container-id
rm .tmp-docker-container-id
```

Then .deb has the application code, dependencies, and configuration wrapped up.
Installing it will put the application in /opt/flask-skeleton and install an
init.d script so you can start the application with `service flask-skeleton
start`.

Deploy the .deb as you see fit.

# Related Works

  1. [sean-/flask-skeleton](https://github.com/sean-/flask-skeleton)
  2. [graup/flask-restless-security](https://github.com/graup/flask-restless-security)
  3. [imwilsonxu/fbone](https://github.com/imwilsonxu/fbone)
  4. [xen/flask-project-template](https://github.com/xen/flask-project-template)
  5. [jelmerdejong/flask-app-blueprint](https://github.com/jelmerdejong/flask-app-blueprint)
  6. [sdetautomation/flask-api](https://github.com/sdetautomation/flask-api)
  7. [cburmeister/flask-bones](https://github.com/cburmeister/flask-bones)
