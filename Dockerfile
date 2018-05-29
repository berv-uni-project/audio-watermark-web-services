# use base python image with python 3.6
FROM python:3.6.5

# ENV HTTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV HTTPS_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV FTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"

# RUN echo "Acquire::http::proxy \"$HTTP_PROXY\";\nAcquire::https::proxy \"$HTTPS_PROXY\";" > /etc/apt/apt.conf

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

