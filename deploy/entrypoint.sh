#!/bin/sh
su app -c 'python3 /app/manage.py collectstatic'
su app -c 'python3 /app/manage.py migrate'
/bin/s6-svscan /etc/services.d
