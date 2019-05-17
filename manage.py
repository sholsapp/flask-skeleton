#!/usr/bin/env python

import datetime

from configobj import ConfigObj
from validate import Validator
from flask_script import Manager
import logging

from flaskskeleton import app, init_webapp
from flaskskeleton.model import db
from flaskskeleton.worker import BackgroundWorker


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


manager = Manager(app)


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
def runserver(*args, **kwargs):
    """Override default `runserver` to init webapp before running."""
    app = init_webapp()
    config = ConfigObj('config/sample.config', configspec='config/sample.configspec')
    app.config_obj = config
    app.run(*args, **kwargs)


if __name__ == "__main__":
    manager.run()
