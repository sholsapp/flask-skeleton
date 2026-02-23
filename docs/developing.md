# Development

Before you get started you'll need to have Python 3.11+ and `uv` installed.

### Setup a Virtual Environment

Create a virtual environment the web application by running the following
commands in a terminal.

#### Initialize Virtual Environment

Using Python 3.11+ and `uv`, create a virtual environment.

```bash
uv sync
```

If you plan on testing, also install the development dependencies.

```
uv sync --group dev
```

### Start the Web Server

Start the Flask development web server on your local machine.

```bash
FLASK_APP="flaskskeleton:init_webapp('./config/dev.config')" flask run
```

Alternatively, start the gunicorn arbiter for a more production-like
environment.

```bash
gunicorn -c config/gunicorn.py -b 0.0.0.0:8080 flaskskeleton:app
```

Then, in your browser, navigate to [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

### (Optional) Initialize the Database

Initialize the development database using alembic.

```bash
alembic upgrade head
```

The database will be created automatically if running in `testing` mode.
Otherwise, you'll need to create it yourself and point to it using the
`SQLALCHEMY_DATABASE_URI` environment variable or configuration file.
``
### (Optional) Start the Worker

Start the background worker process, which uses APScheduler to run
scheduled jobs.

```bash
flask-skeleton-worker -c config/dev.config
```
