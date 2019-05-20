#!/usr/bin/env python

import datetime

from configobj import ConfigObj
from validate import Validator
from flask_script import Manager, Command, Option
import logging

from flaskskeleton import app, init_webapp
from flaskskeleton.model import db
from flaskskeleton.worker import BackgroundWorker


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class GunicornServer(Command):
    """Run the webserver in gunicorn."""
    def get_options(self):
        from gunicorn.config import make_settings
        settings = make_settings()
        options = []
        for setting, klass in settings.items():
            if klass.cli:
                if klass.const is not None:
                    options.append(Option(*klass.cli, const=klass.const, action=klass.action))
                else:
                    options.append(Option(*klass.cli, action=klass.action))
        return options

    def run(self, *args, **kwargs):
        from gunicorn.app.wsgiapp import WSGIApplication
        app = WSGIApplication()
        app.app_uri = 'manage:app'
        return app.run()


manager = Manager(app)

manager.add_command("gunicorn", GunicornServer())


@manager.command
def start_background_worker():
    """Start the background worker."""
    worker = BackgroundWorker(interval=1)
    log.info('Starting worker. Hit CTRL-C to exit!')
    worker.start()
    while worker.is_alive():
        try:
            worker.join(1)
        except KeyboardInterrupt:
            log.info('Shutting down worker thread!')
            worker.stop()


@manager.command
def prime_database():
    """Prime database with some fake data."""
    init_webapp()
    # ...


@manager.command
def runserver(host="127.0.0.1", port="5000"):
    """Override default `runserver` to init webapp before running."""
    app = init_webapp()
    config = ConfigObj('config/sample.config', configspec='config/sample.configspec')
    app.config_obj = config
    app.run(host=host, port=int(port))


if __name__ == "__main__":
    manager.run()
