import pytest
from flask import Flask

from flaskskeleton import init_webapp


@pytest.fixture(scope='module')
def app(request):
    app = Flask(__name__)
    app.config['SERVER_NAME'] = 'localhost'
    app = init_webapp(test=True)
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app
