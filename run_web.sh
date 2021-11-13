#!/bin/sh

# for cleaning up, just used, when in developing
# su -m audiomaster -c "python manage.py reset_migrations web_services"
# prepare init migration
su -m audiomaster -c "python manage.py makemigrations web_services"
# migrate db, so we have the latest db schema
su -m audiomaster -c "python manage.py migrate"
# run with gunicorn
su -m audiomaster -c "gunicorn audio_watermark_web_services"
