# use base python image with python 3.8
FROM python:3.10-slim as build
# set working directory to /app/
WORKDIR /app/
RUN apt-get update && apt-get -y dist-upgrade && apt install -y \
    wget \
    libpng-dev \
    gcc python3-dev \
    musl-dev postgresql-client \
    ffmpeg libsndfile-dev \
    gfortran \
    libopenblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*
# add requirements.txt to the image
ADD requirements.txt requirements.txt
# install python dependencies
RUN pip install -r requirements.txt
COPY . .
# create unprivileged user
RUN adduser --disabled-password --gecos '' audiomaster
