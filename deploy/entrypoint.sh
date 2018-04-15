#!/bin/sh
su app -c 'python3 /app/manage.py collectstatic'
su app -c 'python3 /app/manage.py migrate'

busybox tail -F \
    /var/log/gunicorn/access.log \
    /var/log/gunicorn/error.log \
    /var/log/nginx/access.log \
    /var/log/nginx/error.log \
    &

/bin/s6-svscan /etc/services.d
