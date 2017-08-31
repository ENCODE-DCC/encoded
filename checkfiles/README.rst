Check Files
===========

Files are checked to see if the MD5 sum (both for gzipped and ungzipped) is identical to the submitted metadata, as well as run through
the validateFiles program from jksrc  (https://github.com/ENCODE-DCC/kentUtils/raw/master/bin/linux.x86_64/validateFiles).
It operates on files in the 'uploading' state (according to the encodeD database) in the encode-files S3 bucket.
Checkfiles is used by the ENCODE DCC to validate genomic datafiles submitted by labs.
The bucket itself is mounted using Goofys (https://github.com/kahing/goofys).
Errors are reported back to encodeD.

Setup
-----

Install required packages for running deploy::

    pyvenv .
    bin/pip install -r requirements-deploy.txt

Deploy
------

Supply arguments for checkfiles after a ``--`` separator::

    bin/python deploy.py -- --username ACCESS_KEY_ID --password SECRET_ACCESS_KEY --bot-token SLACK-BOT-TOKEN https://www.encodeproject.org
