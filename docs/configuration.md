# Configuration

This document dissects how this webapp is configured and some of the supporting
files that we use for development or deployment.

### Application Configuration

Let's look at the `config` directory.

```
config
├── dev.config
├── dev.configspec
├── gunicorn.py
└── noaa-api.init
```

These files are the files that make up our application configuration that Flask
and Gunicorn use to configure and start the web application. We also store our
init.d scripts here.

### Debian Package Configuration

Let's look at the `debian` directory.

```
debian
├── changelog
├── compat
├── control
├── install
├── noaa-api.triggers
├── postinst
├── preinst
└── rules
```

These files are the inputs to creating a Debian package, which we use to
package our webapp for deployment. These files express dependencies, use
dh-virtualenv to package a Python virtualenv, package application
configuration, and more. Spend some time and read through these files to see
how we configure the deployment host.

You can read about all of these files and more at
https://www.debian.org/doc/manuals/maint-guide/.
