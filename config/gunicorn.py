#!/usr/bin/env python

from flaskheroku import init_webapp

host = '0.0.0.0'
port = 5000
bind = '%s:%s' % (host, port)
workers = 2

def on_starting(server):
  server.log.setup(server.app.cfg)

def post_fork(server, worker):
  init_webapp()
