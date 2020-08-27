# use base python image with python 3.8
FROM python:3.8 as build
# set working directory to /app/
WORKDIR /app/
RUN apt update && apt -y dist-upgrade && apt install -y \
    build-base wget \
    freetype-dev libpng-dev openblas-dev \
    gcc python3-dev \
    musl-dev postgresql-dev \
    ffmpeg libsndfile-dev \
    && rm -rf /var/lib/apt/lists/*
# add requirements.txt to the image
ADD requirements.txt requirements.txt
# install python dependencies
RUN pip install -r requirements.txt
COPY . .
# create unprivileged user
RUN adduser --disabled-password --gecos '' audiomaster
