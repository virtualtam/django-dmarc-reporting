"""django-dmarc-reporting - Gunicorn configuration

For a list of available settings, see:
http://docs.gunicorn.org/en/latest/settings.html
"""
# pylint: disable=invalid-name
import os

LOG_DIR = os.path.join(os.path.sep, 'var', 'log', 'gunicorn')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

loglevel = 'info'
accesslog = os.path.join(LOG_DIR, 'access.log')
errorlog = os.path.join(LOG_DIR, 'error.log')

bind = 'unix:/var/run/gunicorn.sock'
chdir = os.path.join(os.path.sep, 'app')

user = 'app'
group = 'app'
