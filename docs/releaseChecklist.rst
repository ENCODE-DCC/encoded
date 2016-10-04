Checkout master
    tag it the version number and RC number


git tag -a v[XX]rc[X] -m "a comment"

push tag
    git push origin v[XX]rc[X]

Use a c4.8xlarge
Make DEMO instance with that tag -b v[xx]rc[x]
    bin/deploy -b v[XX]rc[X] -n v[XX]rc[X]

bin/deploy -b v48 --elasticsearch yes --cluster-name v48-cluster --cluster-size 5 --profile-name production --name v{XX}-data --instance-type m4.xlarge

bin/deploy -b v{XX}.0 -n v{XX}-master --cluster-name v{XX}-cluster --profile-name production --candidate --instance-type c4.8xlarge

Wait a few mins then tail the log

When everything has come up change all tickets for this version to deployed in RC.

Log into existing instance: (ubuntu@v{YY}.production.encodedcc.org) - {XX} is the new version number

$ sudo -i -u postgres /opt/wal-e/bin/envfile --config ~postgres/.aws/credentials --section default --upper -- /opt/wal-e/bin/wal-e --s3-prefix="$(cat /etc/postgresql/9.3/main/wale_s3_prefix)" backup-push /var/lib/postgresql/9.3/main

In a clean checkout of master

$ git tag -am v{XX}.0 v{XX}.0
$ git push -u origin v{XX}.0

For a single, combined (ES/Python 1 datanode) instance
===============================
$ bin/deploy --candidate --instance-type c4.4xlarge --profile-name production -n v{XX}-b v{XX}.0

"production" must be a key on encode-prod AWS project with valid key/password in .aws/credentials

$ bin/deploy --test --instance-type c4.4xlarge -n v{XX}-test -b v{XX}.0 --- See Last section

Or just as a demo instance to avoid the switchover

$ bin/deploy --instance-type c4.4xlarge -n v{XX}-test -b v{XX}.0

For a clustered instance - 5 data nodes (current production as of 5/2016)
================================
$ bin/deploy -b v{XX}.0 --elasticsearch yes --cluster-name v{XX}-cluster --cluster-size 5 --profile-name production --name v{XX}-data --instance-type m4.xlarge
$ bin/deploy -b v{XX}.0 -n v{XX}-master --cluster-name v{XX}-cluster --profile-name production --candidate --instance-type c4.8xlarge

"production" must be a key on encode-prod AWS project with valid key/password in .aws/credentials

Once the master is up, you can run:
$ curl localhost:9200/_cluster/health?pretty

To make sure any cluster nodes are running correctly, and swap them out if necessary.
You can create a single node with something like:
$ bin/deploy -b v{XX}.0 --elasticsearch yes --cluster-name v{XX}-cluster --cluster-size 1 --profile-name production --name v{XX}-dataX --instance-type m4.xlarge

Where X is the node you just terminated. Note cluster names must match!

and for DEV (non candidate/--test just as demo)
$ bin/deploy -b v{XX}.0 --elasticsearch yes --cluster-name v{XX}-test-cluster --cluster-size 5 --name v{XX}-test-data --instance-type m4.xlarge
$ bin/deploy -b v{XX}.0 -n v{XX}-test-master --cluster-name v{XX}-test-cluster --instance-type c4.8xlarge

To set replicas (this should move to automatic installation):
$ curl -XPUT 'localhost:9200/_all/_settings' -d '{"index": {"number_of_replicas": 2}}'

This will set cluster status to "yellow"; probably best to wait for green for full release.

== Create and install keys ==

THis is all done only on the master node, v{XX}-master.production.encodedcc.org

Go to the AWS console and create new write-encoded-backups-prod access key and add to new instance ~postgres/.aws/credentials (write-encode-backups and upload-encode-files are AWS users; they can each only have 2 keys so you have to delete the old inactive ones)
$ sudo -u postgres mkdir ~postgres/.aws
$ sudo -u postgres touch ~postgres/.aws/credentials
$ sudo -u postgres chmod o-r ~postgres/.aws/credentials
$ sudo -u postgres nano ~postgres/.aws/credentials

Create new upload-encode-files access key
$ sudo -u encoded nano ~encoded/.aws/credentials

# Set these new keys inaactive

# Send email to ENCODE_DEVELOPERS@LIST.NIH.GOV announcing write downtime (currently 15-20 min)

On the Old production instance:
$ sudo mv /var/lib/postgresql/9.3/main/recovery.done /var/lib/postgresql/9.3/main/recovery.conf
$ sudo service postgresql restart

# downsize test server to m4.xlarge, wait until dns is active

# Edit nginx proxy server (encode-proxy.stanford.edu)
ubuntu@ip-172-31-31-254:~$ sudo nano /etc/nginx/nginx.conf
ubuntu@ip-172-31-31-254:~$ sudo service nginx reload

# Edit BACKUP proxy in case Stanford fails us. proxy.production.encodedcc.org

ubuntu@ip-172-31-41-227:~$ sudo nano /etc/nginx/nginx.conf # switch server backend
ubuntu@ip-172-31-41-227:~$ sudo service nginx reload

 * Reloading nginx configuration nginx

Make old aws access key inactive

Make new aws access key active

Wait for /_indexer snapshot on new instance to match snapshot on old instance
(both should be status: "waiting" and recovery: true)

# - echo "include 'master.conf'" | sudo tee -a /etc/postgresql/9.3/main/postgresql.conf
# - sudo pg_ctlcluster 9.3 main reload
# - sudo pg_ctlcluster 9.3 main promote
# - cd /srv/encoded
# - sudo -i -u encoded bin/batchupgrade production.ini --app-name app
# - sudo -i -u postgres /opt/wal-e/bin/envfile --config ~postgres/.aws/credentials --section default --upper -- /opt/wal-e/bin/wal-e --s3-prefix="$(cat /etc/postgresql/9.3/main/wale_s3_prefix)" backup-push /var/lib/postgresql/9.3/main

# Save logs from old instance

$ mkdir v{YY}
$ scp -r v{YY}.production.encodedcc.org:/var/log/apache2 v{YY}/apache2
$ aws --profile production s3 cp --recursive v{YY} s3://encoded-logs/production/v{YY}

# Add Wal-e backup to S3 via Crontab
$ sudo crontab -e
select nano
add this line for midnight updates

$ 00 7 * * * sudo -i -u postgres /opt/wal-e/bin/envfile --config ~postgres/.aws/credentials --section default --upper -- /opt/wal-e/bin/wal-e --s3-prefix="$(cat /etc/postgresql/9.3/main/wale_s3_prefix)" backup-push /var/lib/postgresql/9.3/main

save and close

add escluster to tags

Update test server IF it was started as --test; demo mode is already Master
===========================================================================

Doing this after bin/batchupgrade on production means no need to do that here too (changes come through postgres replication.)

# New test instance

ubuntu@ip-172-31-1-25:~$ sudo nano /etc/postgresql/9.3/main/custom.conf # archive_mode = off
ubuntu@ip-172-31-1-25:~$ sudo pg_ctlcluster 9.3 main reload
ubuntu@ip-172-31-1-25:~$ sudo pg_ctlcluster 9.3 main promote

Crontab
Dashboard for all cluster

After the release is completely deployed to production:

* log in to redmine at the admin encode-admin
* http://redmine.encodedcc.org/projects/pipeline/issues?query_id=96  needs to be edited to have the next release
* all "release ready" items on this list http://redmine.encodedcc.org/projects/pipeline/issues?query_id=43  need to be updated to closed
* http://redmine.encodedcc.org/projects/pipeline/issues?query_id=43 then needs to be edited to have the next release
* This list *should* be empty http://redmine.encodedcc.org/projects/pipeline/issues?query_id=52,  when it is not, all assignees on the list need to be bothered
* When the list is empty
*** http://redmine.encodedcc.org/projects/pipeline/roadmap  should have all previous versions closed
*** http://redmine.encodedcc.org/projects/pipeline/issues?query_id=52 should be edited to the new version
Update seraches for new version,
     in all searches Release upcoming, Release Summary, and release detail when clicked go to edit in the upper right hand side of the toll bar then edit the filter for public so everyone when they click on the link then gets transferred to the correct version number.
