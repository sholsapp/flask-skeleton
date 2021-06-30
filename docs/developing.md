# Development

Before you get started you'll need to have Python 3.6+ installed. After, you'll
need to also instal virtualenv. Research how to do this for whatever platform
you run before continuing.

### Setup a Virtual Environment

Create a virtual environment the web application by running the following
commands in a terminal.

#### Python 3.6

```bash
python3 -m venv my-venv
source my-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python setup.py develop
```

If you plan on testing, also install the extras.

```
pip install -r requirements-dev.txt
```

Or,

```
pip install -e ".[testing]"
```

### Initialize the Database

Initialize the development database using alembic.

```
alembic upgrade head
```

### Start the Web Server

Start the Flask development web server on your local machine.

```bash
FLASK_APP="flaskskeleton:init_webapp('./config/dev.config')" flask run
```

Alternatively, start the gunicorn arbiter for a more production-like
environment.

```bash
gunicorn -c config/gunicorn.py -b 0.0.0.0:5000 flaskskeleton:app
```

Then, in your browser, navigate to
[http://127.0.0.1:5000/](http://127.0.0.1:5000/).
