#!/bin/sh

# wait for PSQL server to start
sleep 10

# for cleaning up, just used, when in developing
# su -m audiomaster -c "python manage.py reset_migrations web_services"
# prepare init migration
su -m audiomaster -c "python manage.py makemigrations web_services"
# migrate db, so we have the latest db schema
su -m audiomaster -c "python manage.py migrate"  
# start development server on public ip interface, on port 8000
su -m audiomaster -c "python manage.py runserver 0.0.0.0:8000"  
