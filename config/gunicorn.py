#!/usr/bin/env python

from flaskheroku import init_webapp


workers = 2


def on_starting(server):
  server.log.setup(server.app.cfg)


def post_fork(server, worker):
  init_webapp()
