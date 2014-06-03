Demo Machines
=============

To launch a demo machine you need an access key (ask me to create one) which you place in ~/.boto::

    [Credentials]
    aws_access_key_id=AKIA...
    aws_secret_access_key=abc123...
    region = us-west-1

To login to a demo machine, we first need to sign your ssh public key (the one uploaded to github, normally ~/.ssh/id_rsa.pub) with the demo_users_ca private key. This creates an id_rsa-cert.pub which you should place in your ~/.ssh/ alongside your keypair.

You can then ssh into the demo machine::

    $ ssh ubuntu@ec2...compute.amazonaws.com


Authorization of Demo Machines
==============================

Demo machines restore their database from the current Postgres WAL archive stored in S3 by WAL-E.
The demo machines are granted read access via `IAM roles`_ assigned to them by the deploy script.

.. _IAM roles: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html
