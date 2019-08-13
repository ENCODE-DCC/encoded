#!/bin/bash
# Setup postgres 9.3,
#   install wal-e,
#   run backup fetch
# postgres user
# apt deps:
#   postgresql-9.3
#   python2.7-dev # wal-e
#   lzop # wal-e

standby_mode="$1"
ROLE="$2"
WALE_S3_PREFIX="$3"

AWS_CREDS_DIR='/var/lib/postgresql/.aws'
AWS_PROFILE='default'

PG_CONF_DEST='/etc/postgresql/9.3/main'
PG_CONF_SRC='/home/ubuntu/encoded/cloud-config/deploy-run-scripts/conf-pg93'
PG_DATA='/var/lib/postgresql/9.3/main'

WALE_DIR='/opt/wal-e'
WALE_BIN="$WALE_DIR/bin"
WALE_REQS='/home/ubuntu/encoded/wal-e-requirements.txt'


function copy_with_permission {
    src_file="$1/$3"
    dest_file="$2/$3"
    sudo -u root cp "$src_file" "$dest_file"
    sudo -u root chown postgres:postgres "$dest_file"
}


function append_with_user {
  line="$1"
  user="$2"
  dest="$3"
  echo "$line" | sudo -u $user tee -a $dest
}


# Copy pg confs to pg conf dir
for filename in 'custom.conf' 'demo.conf' 'master.conf' 'recovery.conf' ; do
    copy_with_permission "$PG_CONF_SRC" "$PG_CONF_DEST" "$filename"
done

# Update Confs
##master.conf: TODO: Only production needs wal-e push ability? Move to ROLE='candidate'?"
wale_push_cmd="archive_command = '$WALE_BIN/envfile --config $AWS_CREDS_DIR/credentials --section $AWS_PROFILE --upper -- $WALE_BIN/wal-e --s3-prefix=$WALE_S3_PREFIX wal-push \"%p\"'"
append_with_user "$wale_push_cmd" 'postgres' "$PG_CONF_DEST/master.conf"
##recovery.conf
wale_fetch_cmd="restore_command = '$WALE_BIN/wal-e --aws-instance-profile --s3-prefix=$WALE_S3_PREFIX wal-fetch \"%f\" \"%p\"'"
standby_mode_cmd="standby_mode = $standby_mode"
append_with_user "$wale_fetch_cmd" 'postgres' "$PG_CONF_DEST/recovery.conf"
append_with_user "$standby_mode_cmd" 'postgres' "$PG_CONF_DEST/recovery.conf"
##postgresql.conf
include_custom="include 'custom.conf'"
append_with_user "$include_custom" 'postgres' "$PG_CONF_DEST/postgresql.conf"
if [ "$ROLE" == 'candidate' ]; then
    echo 'Candidate'
else
  include_demo="include 'demo.conf'"
  append_with_user "$include_demo" 'postgres' "$PG_CONF_DEST/postgresql.conf"
fi
##WALE_S3_PREFIX
include_custom="include 'custom.conf'"
append_with_user "$WALE_S3_PREFIX" 'root' "$PG_CONF_DEST/wale_s3_prefix"

# Create db prior to wal-e backup fetch
sudo -u postgres createuser encoded
sudo -u postgres createdb --owner=encoded encoded

# Install wal-e
sudo -u root mkdir "$WALE_DIR"
sudo -u root chown postgres:postgres "$WALE_DIR"
cd "$WALE_DIR"
cp $WALE_REQS ./wal-e-requirements.txt
sudo -u postgres virtualenv --python=python2.7 ./
sudo -u postgres "$WALE_BIN/pip" install -r ./wal-e-requirements.txt

# Update db from wale backup
sudo -u postgres /etc/init.d/postgresql stop
sudo -u postgres "$WALE_BIN/wal-e" --aws-instance-profile --s3-prefix="$WALE_S3_PREFIX" backup-fetch "$PG_DATA" LATEST

# Set db to recoery mode:
#  TODO: backup-fetch doesnot use recovery(wale-fetch) like
# backup-push uses wal-push?
sudo -u postgres ln -s "$PG_CONF_DEST/recovery.conf" "$PG_DATA/"

# Restart db to update conf
sudo -u postgres /etc/init.d/postgresql start

# Wait - TODO: Move to main script?
until sudo -u postgres psql postgres -c ""; do sleep 10; done
