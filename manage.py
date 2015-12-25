#!/usr/bin/env python

from configobj import ConfigObj
from validate import Validator
from flask.ext.script import Manager
import logging

from flaskskeleton import app, init_webapp
from flaskskeleton.model import db, Employee
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
  db.session.add(Employee('Bob', 'Smith', 'Software Engineer', 50000))
  db.session.add(Employee('Alice', 'Johnson', 'Software Engineer', 50000))
  db.session.commit()


@manager.command
def runserver(*args, **kwargs):
  """Override default `runserver` to init webapp before running."""
  app = init_webapp()
  # TODO(sholsapp): parameterize this, but don't clobber the *args, **kwargs
  # space, because it's annoying to have to pass these in to the `run` method.
  config = ConfigObj('config/sample.config', configspec='config/sample.configspec')
  app.config_obj = config
  app.run(*args, **kwargs)


if __name__ == "__main__":
  manager.run()
