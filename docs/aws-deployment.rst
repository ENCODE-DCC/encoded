
Log into existing instance: (ubuntu@v{YY}.production.encodedcc.org) - {XX} is the new version number

$ sudo -i -u postgres /opt/wal-e/bin/envfile --config ~postgres/.aws/credentials --section default --upper -- /opt/wal-e/bin/wal-e --s3-prefix="$(cat /etc/postgresql/9.3/main/wale_s3_prefix)" backup-push /var/lib/postgresql/9.3/main

In a clean checkout of master

$ git tag -am v{XX}.0 v{XX}.0
$ git push -u origin v{XX}.0

$ bin/deploy --candidate --instance-type c4.4xlarge --profile-name production -n v{XX}-b v{XX}.0

"production" must be a key on encode-prod AWS project with valid key/password in .aws/credentials

$ bin/deploy --test --instance-type c4.4xlarge -n v{XX}-test -b v{XX}.0  --- See Last section

Or just as a demo instance to avoid the switchover

$ bin/deploy --instance-type c4.4xlarge -n v{XX}-test -b v{XX}.0


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

# Edit BACKUP proxy in case Stanford fails us.  proxy.production.encodedcc.org

ubuntu@ip-172-31-41-227:~$ sudo nano /etc/nginx/nginx.conf  # switch server backend
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




Update test server IF it was started as --test; demo mode is already Master
===========================================================================

Doing this after bin/batchupgrade on production means no need to do that here too (changes come through postgres replication.)


# New test instance

ubuntu@ip-172-31-1-25:~$ sudo nano /etc/postgresql/9.3/main/custom.conf   # archive_mode = off
ubuntu@ip-172-31-1-25:~$ sudo pg_ctlcluster 9.3 main reload
ubuntu@ip-172-31-1-25:~$ sudo pg_ctlcluster 9.3 main promote


