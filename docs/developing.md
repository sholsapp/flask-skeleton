# Development

Before you get started you'll need to have Python 2.7+ or Python 3.6+
installed. After, you'll need to also instal virtualenv. Research how to do
this for whatever platform you run before continuing.

### Setup a Virtual Environment

Create a virtual environment the web application by running the following
commands in a terminal.

#### Python 2.7

```bash
virtualenv my-venv
source my-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python setup.py develop
```

#### Python 3.6

```bash
python3 -m venv my-venv
source my-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python setup.py develop
```

### Start the Web Server

Start the Flask development web server on your local machine using
Flask-Manager.

```bash
./manage.py runserver --host 127.0.0.1 --port 5000
```

Alternatively, start the gunicorn arbiter for a more production-like
environment.

```bash
./manage.py gunicorn -c conf/gunicorn.py
```

Then, in your browser, navigate to
[http://127.0.0.1:5000/](http://127.0.0.1:5000/). Or, using your CLI, use curl
and jq to inspect the JSON API that follows [JSON
Schema](http://json-schema.org/).
