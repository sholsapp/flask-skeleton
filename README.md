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

Out of the box, it comes with a simple OAuth2 integration against Google Calendar API.
If you want to use this integration, you'll need to follow the directions
[here](https://developers.google.com/calendar/auth) to setup an application on
your Google API Console. Export the client/secret to
`GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`, respectively. Again, if you don't
want this integration, just delete the code.

## development

Before you get started you'll need to have Python 2.7+ installed. After, you'll
need to also instal virtualenv. Research how to do this for whatever platform
you run before continuing.

### setup a virtualenv

Create a virtual environment the web application by running the following
commands in a terminal.

```bash
virtualenv my-venv
source my-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python setup.py develop
```

### start the web server

Start the web server on your local machine using Flask-Manager.

```bash
./manage.py runserver
```

Then, in your browser, navigate to
[http://127.0.0.1:5000/](http://127.0.0.1:5000/). Then, on your CLI, use curl
and jq to inspect the JSON API that follows [JSON
Schema](http://json-schema.org/).

![Using curl to inspect the JSON API](./data/api.png).

# Related Works

Also see:

  1. [sean-/flask-skeleton](https://github.com/sean-/flask-skeleton)
