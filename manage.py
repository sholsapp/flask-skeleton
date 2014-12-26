#!/usr/bin/env python

from configobj import ConfigObj
from validate import Validator
from flask.ext.script import Manager

from flaskskeleton import app, init_webapp
from flaskskeleton.model import db, Messages


manager = Manager(app)


@manager.command
def prime_database():
  """Prime database with some fake data."""
  init_webapp()
  for message in ['a', 'b', 'c', 'd', 'e']:
    m = Messages(message * 64)
    db.session.add(m)
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
