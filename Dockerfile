FROM ubuntu
RUN apt-get update
RUN apt-get --assume-yes install \
    python-dev \
    python-setuptools \
    python-pip \
    build-essential
WORKDIR /build/
COPY requirements.txt /build/
RUN pip install -r requirements.txt
COPY setup.py README.md manage.py /build/
COPY flaskskeleton /build/flaskskeleton
COPY config /build/config
RUN python setup.py install
EXPOSE 5000
CMD ["./manage.py", "runserver", "--host", "0.0.0.0", "--port", "5000"]
