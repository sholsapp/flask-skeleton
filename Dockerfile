# Builder builds a debian package.
FROM ubuntu:25.10 AS builder
RUN apt-get update
RUN apt-get --assume-yes install \
    build-essential \
    debhelper \
    devscripts \
    dh-virtualenv \
    equivs \
    libssl-dev \
    pipx \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv
RUN pipx install uv
WORKDIR /build/flask-skeleton
COPY uv.lock /build/flask-skeleton
COPY pyproject.toml README.md /build/flask-skeleton/
COPY debian /build/flask-skeleton/debian
COPY flaskskeleton /build/flask-skeleton/flaskskeleton
COPY config /build/flask-skeleton/config
RUN dpkg-buildpackage -us -uc -b

# This builds a runnable development server.
FROM ubuntu:25.10
WORKDIR /tmp
RUN apt-get update
RUN apt-get --assume-yes install \
    python3 \
    sudo
COPY --from=builder /build/* /tmp
RUN dpkg -i /tmp/flask-skeleton_0.1-1_*.deb
CMD service flask-skeleton restart && tail -F /opt/flask-skeleton/var/log/flask-skeleton.log
