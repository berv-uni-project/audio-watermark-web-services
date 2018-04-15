# use base python image with python 3.6
FROM python:3.6.5

# add requirements.txt to the image
ADD requirements.txt /app/requirements.txt

# set working directory to /app/
WORKDIR /app/

# install python dependencies
RUN pip install -r requirements.txt

# create unprivileged user
RUN adduser --disabled-password --gecos '' audiomaster

# install ffmpeg 
RUN apt-get update
RUN apt-get -y install libav-tools libsndfile1

