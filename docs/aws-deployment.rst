
Log into existing instance:

$ sudo -i -u postgres /opt/wal-e/bin/wal-e --aws-profile default --s3-prefix="$(cat /etc/postgresql/9.3/main/wale_s3_prefix | tr -d "\n")" backup-push /var/lib/postgresql/9.3/main

$ git tag -am v35.0 v35.0
$ git push -u origin v35.0

$ bin/deploy --candidate --instance-type c4.4xlarge --profile-name production -n v35 -b v35.0

$ bin/deploy --test --instance-type c4.4xlarge -n v26-test -b v24.0

Or just as a demo instance to avoid the switchover

$ bin/deploy --instance-type c4.4xlarge -n v35-test -b v35.0


Go to the AWS console and create new write-encoded-backups-prod access key and add to new instance ~postgres/.aws/credentials
$ sudo -u postgres mkdir ~postgres/.aws
$ sudo -u postgres touch ~postgres/.aws/credentials
$ sudo -u postgres chmod o-r ~postgres/.aws/credentials
$ sudo -u postgres nano ~postgres/.aws/credentials

Create new upload-encode-files access key
$ sudo -u encoded nano ~encoded/.aws/credentials

Old
$ sudo mv /var/lib/postgresql/9.3/main/recovery.done /var/lib/postgresql/9.3/main/recovery.conf
$ sudo service postgresql restart


# Edit nginx proxy server
ubuntu@ip-172-31-31-254:~$ sudo nano /etc/nginx/nginx.conf
ubuntu@ip-172-31-31-254:~$ sudo service nginx reload
 * Reloading nginx configuration nginx


Make old aws access key inactive

Make new aws access key active

Wait for /_indexer snapshot on new instance to match snapshot on old instance

# - echo "include 'master.conf'" | sudo tee -a /etc/postgresql/9.3/main/postgresql.conf
# - sudo pg_ctlcluster 9.3 main reload
# - sudo pg_ctlcluster 9.3 main promote
# - cd /srv/encoded
# - sudo -i -u encoded bin/batchupgrade production.ini --app-name app
# - sudo -i -u postgres /opt/wal-e/bin/wal-e --aws-profile default --s3-prefix="$(cat /etc/postgresql/9.3/main/wale_s3_prefix | tr -d "\n")" backup-push /var/lib/postgresql/9.3/main


# Save logs

$ mkdir v34
$ scp -r v34.production.encodedcc.org:/var/log/apache2 v34/apache2
$ aws --profile production s3 cp --recursive v34 s3://encoded-logs/production/v34


Update test server
==================

Doing this after bin/batchupgrade on production means no need to do that here too (changes come through postgres replication.)


# nginx-test.demo.encodedcc.org

ubuntu@ip-172-31-41-227:~$ sudo nano /etc/nginx/nginx.conf  # switch server backend
ubuntu@ip-172-31-41-227:~$ sudo service nginx reload

# New test instance

ubuntu@ip-172-31-1-25:~$ sudo nano /etc/postgresql/9.3/main/custom.conf   # archive_mode = off
ubuntu@ip-172-31-1-25:~$ sudo pg_ctlcluster 9.3 main reload
ubuntu@ip-172-31-1-25:~$ sudo pg_ctlcluster 9.3 main promote

