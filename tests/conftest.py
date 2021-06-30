import pytest
from flask import Flask
from pytest_flask.fixtures import client

from flaskskeleton import init_webapp

assert client


@pytest.fixture(scope="module")
def app(request):
    app = Flask(__name__)
    config = {
        "webapp": {
            "host": "localhost",
            "port": "5000",
            "database_uri": "sqlite://",
        }
    }
    app = init_webapp(config, test=True)
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app
