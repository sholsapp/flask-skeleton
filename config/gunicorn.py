#!/usr/bin/env python

from configobj import ConfigObj

from flaskskeleton import init_webapp


configobj_path = 'config/dev.config'
configobj = ConfigObj(configobj_path, configspec=f"{configobj_path}spec")

host = configobj['webapp']['host']
port = configobj['webapp']['port']

#: The bind address.
bind = f'{host}:{port}'

#: The number of web workers.
workers = 2

#: The log level.
log_level = 'info'

#: The Access log file to write to.
accesslog = '-'

#: The Error log file to write to.
errorlog = '-'

#: Redirect stdout/stderr to Error log.
capture_output = True


def on_starting(server):
    server.log.setup(server.app.cfg)
    server.app.configobj_path = configobj_path


def post_fork(server, worker):
    init_webapp(server.app.configobj_path)
