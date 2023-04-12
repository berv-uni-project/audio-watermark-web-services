# use base python image with python 3.8
FROM python:3.11.3-slim as build
# ENV HTTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV HTTPS_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# ENV FTP_PROXY "http://bervianto.leo:03515380@cache.itb.ac.id:8080"
# RUN echo "Acquire::http::proxy \"$HTTP_PROXY\";\nAcquire::https::proxy \"$HTTPS_PROXY\";" > /etc/apt/apt.conf
# set working directory to /app/
WORKDIR /app/
ADD requirements-web.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN adduser --disabled-password --gecos '' audiomaster
