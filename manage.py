#!/usr/bin/env python

from flask.ext.script import Manager

from flaskheroku import app, init_webapp


manager = Manager(app)


@manager.command
def runserver(*args, **kwargs):
  """Override default `runserver` to init webapp before running."""
  app = init_webapp()
  app.run(*args, **kwargs)


if __name__ == "__main__":
  manager.run()
