Demo Machines
=============

To launch a demo machine you need an access key (log into AWS console to create one under IAM) which you place in ``~/.aws/credentials`` (see _aws getting started) which is shared with the aws cli utility::

    [default]
    aws_access_key_id=AKIA...
    aws_secret_access_key=abc123...

In ``~/.boto`` configure your default region::

    [Boto]
    ec2_region_name = us-west-2

To deploy your currently checked out branch, run::

    $ bin/deploy   --instance-type c4.8xlarge

After a few moments, it will return the domain name of your instance::

Initial indexing currently requires c4.8xlarge, but after indexing stop instance at console and restart it with an m4.xlarge if you are not doing any major patches or indexing tests.

    branchname-789abc-username.instance.encodedcc.org

The deployment can take some time, especially if it's been a while since the last full database backup.

Once the demo is indexed ratchet down the instance size
  * Login to https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#Instances:sort=instanceState
  * Select your instance
  * Select Action - Instance State - Stop
  * Select Action - Instance Settings - Change Instance Type

To login to a demo machine, DCC devops team first needs to `sign your ssh public key`_ (the one uploaded to github, normally ~/.ssh/id_rsa.pub) with the demo_users_ca private key. This creates an id_rsa-cert.pub which you should place in your ~/.ssh/ alongside your keypair::

    $ ssh-keygen -s demo_users_ca -I user_myusername -n ubuntu -V +520w myusername.pub 

Note that you need a fairly recent version of OpenSSH for this to work, Mac OS 10.6 and CentOS 6.4 are known not to work (though you can install a newer openssh with homebrew) but Ubuntu 14.04 and Mac OS 10.9 do work.   The key needs to be named "parallel" to your private key usually id_rsa-cert.pub (to go with id_rsa).

You can then ssh into the demo machine::

    $ ssh ubuntu@ec2...compute.amazonaws.com

You can then follow the deployment progress with::

    $ tail -f /var/log/cloud-init-output.log

.. _sign your ssh public key: https://www.digitalocean.com/community/articles/how-to-create-an-ssh-ca-to-validate-hosts-and-clients-with-ubuntu

.. _aws getting started: http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html


Authorization of Demo Machines
==============================

Demo machines restore their database from the current Postgres WAL archive stored in S3 by WAL-E.
The demo machines are granted read access via `IAM roles`_ assigned to them by the deploy script.

.. _IAM roles: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html
