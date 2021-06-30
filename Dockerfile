# Builder builds a debian package.
FROM ubuntu:18.04 as builder
RUN apt-get update
RUN apt-get --assume-yes install \
    build-essential \
    debhelper \
    devscripts \
    dh-virtualenv \
    equivs \
    libssl-dev \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools
WORKDIR /build/flask-skeleton
COPY requirements.txt /build/flask-skeleton
COPY setup.py VERSION README.md /build/flask-skeleton/
COPY debian /build/flask-skeleton/debian
COPY flaskskeleton /build/flask-skeleton/flaskskeleton
COPY config /build/flask-skeleton/config
RUN dpkg-buildpackage -us -uc -b

# This builds a runnable development server.
from ubuntu:18.04
WORKDIR /tmp
RUN apt-get update
RUN apt-get --assume-yes install \
    python3 \
    sudo
COPY --from=builder /build/flask-skeleton_0.1-1_amd64.deb /tmp
RUN dpkg -i /tmp/flask-skeleton_0.1-1_amd64.deb
CMD service flask-skeleton restart && tail -F /opt/flask-skeleton/var/log/flask-skeleton.log
