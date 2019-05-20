FROM ubuntu
RUN apt-get update
RUN apt-get --assume-yes install \
    python-dev \
    python-setuptools \
    python-pip \
    build-essential
WORKDIR /build/
COPY . /build/
RUN pip install -r requirements.txt && python setup.py install
EXPOSE 5000
CMD ["./manage.py", "runserver", "--host", "0.0.0.0", "--port", "5000"]
