# flask-heroku

A "hello world" style Flask web server application that (optionally) runs on
Heroku.

Some notable parts used in this web application are:

  1. Flask
  2. Gunicorn
  3. Flask-Restless
  4. Flask-SQLAlchemy
  5. Flask-Bootstrap
  6. Flask-Manager

## development

### setup a virtualenv

Create a virtual environment the web application by running the following
commands in a terminal.

```bash
virtualenv my-venv
source my-venv/bin/activate
python setup.py develop
```
### start the web server

Start the web server on your local machine using Flask-Manager.

```bash
./manage.py runserver
```

Then, in your browser, navigate to http://127.0.0.1:5000/. You should see
something like the following image.

![The flask-heroku application running in a web browser.](data/flask-heroku.jpg)

## heroku

Before you can get started on Heroku, you'll need to have a Heroku account and
their toolchain setup. To do that, follow the instructions at
https://devcenter.heroku.com/articles/quickstart.
