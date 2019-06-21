# use base python image with python 3.7
FROM python:3.7-alpine as build
# ENV HTTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV HTTPS_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV FTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# RUN echo "Acquire::http::proxy \"$HTTP_PROXY\";\nAcquire::https::proxy \"$HTTPS_PROXY\";" > /etc/apt/apt.conf
# set working directory to /app/
WORKDIR /app/
RUN apk update && apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    ffmpeg \
    libsndfile-dev
# add requirements.txt to the image
ADD requirements.txt requirements.txt
# install python dependencies
RUN pip install -r requirements.txt
COPY . .
# create unprivileged user
RUN adduser --disabled-password --gecos '' audiomaster
