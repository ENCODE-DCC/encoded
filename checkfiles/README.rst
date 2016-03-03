Check Files
===========

Setup
-----

Install required packages for running deploy::

    pyvenv .
    bin/pip install -r requirements-deploy.txt

Deploy
------

Supply arguments for checkfiles after a ``--`` separator::

    bin/python deploy.py -- --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY https://www.encodeproject.org
