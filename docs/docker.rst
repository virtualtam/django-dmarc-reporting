Docker Images
=============

Components
----------

- Base OS: `Alpine Linux <https://www.alpinelinux.org/>`_
  (image: `alpine:3.7 <https://store.docker.com/images/alpine>`_)
- WSGI container: `Gunicorn <http://gunicorn.org/>`_
- HTTP server: `Nginx <https://nginx.org/>`_
- Process supervision: `s6 <http://www.skarnet.org/software/s6/index.html>`_
- Database backend: `SQLite <https://sqlite.org/index.html>`_


Building and running
--------------------

Build the images with Compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

  $ cd <path/to/django-dmarc-reporting>
  $ docker-compose build

Start the services with Compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

  $ docker-compose up -d

Create a Django superuser
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

  $ docker exec -ti django-dmarc-reporting_dmarc_1 python3 manage.py createsuperuser

  Username: iamroot
  Email address: i.am@r.oot
  Password:
  Password (again):
  Superuser created successfully.

Display application and server logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: shell

   $ docker-compose logs


Resources
---------

Dockerfile
~~~~~~~~~~

- `Dockerfile reference <https://docs.docker.com/engine/reference/builder/>`_
- `Dockerfile best practices
  <https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/>`_

Data storage and persistence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `Use volumes <https://docs.docker.com/storage/volumes/>`_
- `Volumes reference <https://docs.docker.com/engine/admin/volumes/volumes/>`_

Compose
~~~~~~~

- `Docker Compose <https://docs.docker.com/compose/>`_
- `Getting started with Compose <https://docs.docker.com/compose/gettingstarted/>`_
- `Quickstart: Compose and Django <https://docs.docker.com/compose/django/>`_
- `Compose v3 reference
  <https://docs.docker.com/compose/compose-file/>`_

Django
~~~~~~

- `Project settings <https://docs.djangoproject.com/en/2.0/ref/settings/>`_

Gunicorn
~~~~~~~~

- `Home <http://gunicorn.org/>`_
- `Settings <http://docs.gunicorn.org/en/latest/settings.html>`_

Training
~~~~~~~~

- `Interactive Docker training portal <https://www.katacoda.com/courses/docker/>`_
  on `Katakoda <https://www.katacoda.com/>`_

