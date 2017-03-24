AWS Release and deployment
==========================

1.  #### Pre Release work

    a.  Before a release is made you need to backup the current
        > production servers postgres.

        i.  sudo -i -u postgres /opt/wal-e/bin/envfile --config
            > \~postgres/.aws/credentials --section default --upper --
            > /opt/wal-e/bin/wal-e --s3-prefix="\$(cat
            > /etc/postgresql/9.3/main/wale\_s3\_prefix)" backup-push
            > /var/lib/postgresql/9.3/main

    b.  Turn off fileindexer in production, it will often run for a few
        > days before reporting a result.

2.  #### Create tag for new release

    a.  For the new server we must make a current tag of everything in
        > the master branch. ---NOTE--- Be sure to verify that all
        > merges have been made by contacting the merge admin.

        i.  Checkout master:

            1.  git checkout master

        ii. Pull to make sure all merges are there:

            1.  git pull

        iii. Create tag:

            1.  git tag –am v{XX}.0 v{XX}.0

        iv. Push the newly created tag to origin:

            1.  git push -u origin v{XX}.0

3.  #### Release Type:

    a.  *Single*

        i.  If only a single server is needed for the release, then run
            > the commands below

            1.  For a candidate release that will be used for switch
                > over and will index from production databases

                a.  bin/deploy --candidate --instance-type c4.4xlarge
                    > --profile-name production -n v{XX}-b v{XX}.0

            2.  For a test instance

                a.  bin/deploy --test --instance-type c4.4xlarge -n
                    > v{XX}-test -b v{XX}.0

            3.  To create a demo server to avoid a switchover

                a.  bin/deploy --instance-type c4.4xlarge -n v{XX}-test
                    > -b v{XX}.0

    b.  *Clustered*

        i.  When making a clustered server be sure to follow the order
            > of operations as it does matter.

            1.  Build the clusters

                a.  bin/deploy -b v{XX}.0 --elasticsearch yes
                    > --cluster-name v{XX}-cluster --cluster-size 5
                    > --profile-name production --name v{XX}-data
                    > --instance-type m4.xlarge

            2.  Build the master

                a.  bin/deploy -b v{XX}.0 -n v{XX}-master --cluster-name
                    > v{XX}-cluster --profile-name production
                    > --candidate --instance-type c4.8xlarge

            3.  Login and tail the logs to be sure no errors have
                > occurred

                a.  tail –f /var/log/cloud-init-output.log

            4.  After first automatic restart of the new master be sure
                > that the master can see its cluster

                a.  curl localhost:9200/\_cluster/health?pretty

            5.  If the printout shows yellow or red see whether or not
                > you have a bad node. Or if you have replaced a node
                > run the below command.

                a.  curl -XPUT 'localhost:9200/\_all/\_settings' -d
                    > '{"index": {"number\_of\_replicas": 2}}'

            6.  Check again to see if all nodes are now recognized

                a.  curl localhost:9200/\_cluster/health?pretty

    c.  *Test Server Creation*

        i.  As the production server comes up and checks are being run,
            > now is time to start the test.encode.org server, nothing
            > will need to be done to the servers. Simply bring them up
            > and make sure no errors. This can be done any time
            > after 2.

            1.  Build the Cluster

                a.  bin/deploy -b v{XX} --elasticsearch yes
                    > --cluster-name v{XX}-test-cluster --cluster-size 5
                    > --name v{XX}-test-data --instance-type m4.xlarge

            <!-- -->

            1.  Build the Master

                a.  bin/deploy -b v{XX} -n v{XX}-test-master
                    > --cluster-name v{XX}-test-cluster --instance-type
                    > c4.8xlarge

    <!-- -->

    a.  *Adding and removing nodes from a live system*

        1.  If a cluster node is not being recognized, you can replace
            > it by;

            a.  Terminating or shutting the node down via AWS

            b.  Create a new one by keeping the same cluster name.

                i.  bin/deploy -b v{XX}.0 --elasticsearch yes
                    > --cluster-name v{XX}-cluster --cluster-size 1
                    > --profile-name production --name v{XX}-data{X}
                    > --instance-type m4.xlarge

                ii. dataX being the node number you brought down.

            c.  Then set the replicas

                i.  curl -XPUT 'localhost:9200/\_all/\_settings' -d
                    > '{"index": {"number\_of\_replicas": 2}}'

                ii. Check status to make sure the master sees the
                    > cluster

                iii. curl localhost:9200/\_cluster/health?pretty

4.  #### Create and install Keys

    a.  Stage 1: AWS Key creation and config

        i.  Log into the AWS console for production and navigate to the
            > IAM console and go to users

            1.  In users look for “write-encoded-backups”

                a.  Delete the current INACTIVE key and create a new
                    > key. Be sure to also download the new key
                    > credentials. Once made set it to inactive.

            2.  In users look for “upload-encode-files”

                a.  Delete the current INACTIVE key and create a new
                    > key. Be sure to also download the new key
                    > credentials. Once made set it to inactive.

        ii. Log into the NEW master and now set the /.aws/credentials to
            > the new credentials for write-encode-backups

            1.  Make the /.aws dir:

                a.  sudo -u postgres mkdir \~postgres/.aws

            2.  Create the credentials file:

                a.  sudo -u postgres touch \~postgres/.aws/credentials

            3.  Change permissions to read and open:

                a.  sudo -u postgres chmod o-r
                    > \~postgres/.aws/credentials

            4.  Edit the credentials file:

                a.  sudo -u postgres nano \~postgres/.aws/credentials

            5.  Credentials format

                a.  \[default\]\
                    > aws\_access\_key\_id = \*\*key\*\*\
                    > aws\_secret\_access\_key = \*\*key\*\*

            6.  Edit the credentials for the upload-encode-files

                a.  sudo -u encoded nano \~encoded/.aws/credentials

                b.  format:\
                    > \[encode-files-upload\]\
                    > aws\_access\_key\_id = \*\*key\*\*\
                    > aws\_secret\_access\_key = \*\*key\*\*

    b.  Edit apache encode.conf

        i.  Turn off fileindexer initially.

        ii. When the production move is completed and had some basic
            > checks (probably by next morning), fileindexer can be
            > turned back on (note this restarts apache so is best done
            > when there isn’t a big indexing job) (see step 15)

5.  #### Wait for NEW master to finish its first big indexing before continuing

    a.  =======WAIT========

    b.  Check to see if there is any activity on the OLD server, best to
        > do this at a low traffic time.

    c.  =======WAIT========

> NOTES: It can happen that there is a large indexing occurring on
> production during the release process. The switch over can still take
> place (the underlying database is what really matters) but it will be
> very difficult to tell that the two sites are synchronized. It is
> usually best to just delay the final steps until the indexing “lag” is
> down to a matter of minutes. You can usually tell by monitoring the
> /\_indexer end points how long a given “bolus” has been indexing
> (although of course, you cannot actually tell when it will finish),
> and how long the last few have taken.

1.  #### Before switch over occurs notify all developers that work with the system that the server will be down for writes.

    a.  Email:
        > [*ENCODE\_DEVELOPERS@LIST.NIH.GOV*](mailto:ENCODE_DEVELOPERS@LIST.NIH.GOV)

2.  #### On the OLD server switch postgres into recovery mode

    a.  sudo mv /var/lib/postgresql/9.3/main/recovery.done
        > /var/lib/postgresql/9.3/main/recovery.conf

    b.  sudo service postgresql restart

3.  #### Switch the proxies

    a.  Stanford Proxy: ip-171.67.205.70

        i.  sudo nano /etc/nginx/nginx.conf

        ii. switch the old server's URL with the new servers and the
            > same for the test server if a new test server has been
            > made

        iii. sudo nginx -s reload

    b.  Backup proxy: ip-52.11.61.187

        i.  sudo nano /etc/nginx/nginx.conf

        ii. switch the old server's’ URL with the new servers and the
            > same for the test server if a new test server has been
            > made

        iii. sudo service nginx reload

    c.  If you use RESTART instead of RELOAD accidentally

        i.  []{#_gjdgxs .anchor}sudo nginx -s reload

4.  #### Switch over keys

    a.  Make both keys on AWS that are active to inactive and the new
        > keys created should now be made active

    b.  Run keyValidation.sh script

5.  ####  WAIT for the snapshot on new server to match the snapshot on the old instance and wait for both to have the status “waiting” and recovery: “true”

6.  ####  Set NEW server as postgres master and promote it

    a.  echo "include 'master.conf'" | sudo tee -a
        > /etc/postgresql/9.3/main/postgresql.conf

    b.  sudo pg\_ctlcluster 9.3 main reload

    c.  sudo pg\_ctlcluster 9.3 main promote

    d.  change to /srv/encoded

        i.  cd /srv/encoded

    e.  batch upgrade

        i.  sudo -i -u encoded bin/batchupgrade production.ini
            > --app-name app

    f.  set back-up push

        i.  sudo -i -u postgres /opt/wal-e/bin/envfile --config
            > \~postgres/.aws/credentials --section default --upper --
            > /opt/wal-e/bin/wal-e --s3-prefix="\$(cat
            > /etc/postgresql/9.3/main/wale\_s3\_prefix)" backup-push
            > /var/lib/postgresql/9.3/main

7.  #### Save logs from old instance and push up

    a.  On your personal machine make a dir for the old logs

        i.  mkdir v{YY}

    b.  SCP the old logs to new dir

        i.  scp -r v{YY}.production.encodedcc.org:/var/log/apache2
            > v{YY}/apache2

    c.  push logs to AWS S3 bucket

        i.  aws --profile production s3 cp --recursive v{YY}
            > s3://encoded-logs/production/v{YY}

8.  #### Add Wal-e backup to crontab on NEW server

    a.  Open crontab editor

        i.  sudo crontab –e

    b.  select nano as editor

    c.  Add this line to the bottom of the crontab file

        i.  00 7 \* \* \* sudo -i -u postgres /opt/wal-e/bin/envfile
            > --config \~postgres/.aws/credentials --section default
            > --upper -- /opt/wal-e/bin/wal-e --s3-prefix="\$(cat
            > /etc/postgresql/9.3/main/wale\_s3\_prefix)" backup-push
            > /var/lib/postgresql/9.3/main

    d.  Save and Close

9.  ####  Set all Redmine “Release Ready” Tickets to closed

10. ####  Turn file indexer back on (if site is pronounced stable)


