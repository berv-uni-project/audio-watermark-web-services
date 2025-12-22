# use base python image with python 3.8
FROM python:3.14.2-slim as build

# ENV HTTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV HTTPS_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV FTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"

# RUN echo "Acquire::http::proxy \"$HTTP_PROXY\";\nAcquire::https::proxy \"$HTTPS_PROXY\";" > /etc/apt/apt.conf

# set working directory to /app/
WORKDIR /app/
# add requirements.txt to the image
ADD requirements-celery.txt requirements.txt

# install python dependencies
RUN pip install -r requirements.txt

COPY . .
# create unprivileged user
RUN adduser --disabled-password --gecos '' audiomaster
# install ffmpeg
RUN apt-get update
RUN apt-get -y install libav-tools libsndfile1


