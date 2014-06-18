Demo Machines
=============

To launch a demo machine you need an access key (log into AWS console to create one under IAM) which you place in ``~/.aws/credentials`` which is shared with the aws cli utility::

    [default]
    aws_access_key_id=AKIA...
    aws_secret_access_key=abc123...

In ``~/.boto`` configure your default region::

    [Boto]
    ec2_region_name = us-west-1

You can then run::

    $ bin/deploy

Which will deploy your currently checked out branch.

To login to a demo machine, we first need to `sign your ssh public key`_ (the one uploaded to github, normally ~/.ssh/id_rsa.pub) with the demo_users_ca private key. This creates an id_rsa-cert.pub which you should place in your ~/.ssh/ alongside your keypair.

Note that you need a fairly recent version of OpenSSH for this to work, Mac OS 10.6 and CentOS 6.4 are known not to work (though you can install a newer openssh with homebrew) but Ubuntu 14.04 and Mac OS 10.9 do work.

You can then ssh into the demo machine::

    $ ssh ubuntu@ec2...compute.amazonaws.com

.. _sign your ssh public key: https://www.digitalocean.com/community/articles/how-to-create-an-ssh-ca-to-validate-hosts-and-clients-with-ubuntu


Authorization of Demo Machines
==============================

Demo machines restore their database from the current Postgres WAL archive stored in S3 by WAL-E.
The demo machines are granted read access via `IAM roles`_ assigned to them by the deploy script.

.. _IAM roles: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html
