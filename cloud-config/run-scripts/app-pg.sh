#!/bin/bash
# Setup postgres 9.3 or 11,
#   install wal-e,
#   run backup fetch
echo -e "\n$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0)"

# Check previous failure flag
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping: encd_failed_flag exits"
    exit 1
fi
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Running"

# Script Below
if [ "$ENCD_BUILD_TYPE" == 'app' ] || [ "$ENCD_BUILD_TYPE" == 'app-es' ]; then
    echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Skipping install for no pg build"
    exit 0
fi
standby_mode="$1"


### Variables
AWS_CREDS_DIR='/var/lib/postgresql/.aws'
AWS_PROFILE='default'

PG_CONF_DEST="/etc/postgresql/$ENCD_PG_VERSION/main"
PG_CONF_SRC="$ENCD_CC_DIR/configs/postgresql"
PG_DATA="/var/lib/postgresql/$ENCD_PG_VERSION/main"

WALE_DIR='/opt/pg-wal-e'
WALE_VENV="$WALE_DIR/.pyenv-wal-e"
WALE_BIN="$WALE_VENV/bin"
WALE_ENV='/etc/wal-e.d/env'
WALE_REQS_SRC="$ENCD_SCRIPTS_DIR/app-pg-wale-pyreqs.txt"
WALE_REQS_DST="$WALE_DIR/app-pg-wale-pyreqs.txt"


### Functions
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


### Configure

echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Setup aws keys for wal-e"

# Downlaod postgres demo aws keys
pg_keys_dir='/home/ubuntu/pg-aws-keys'
mkdir "$pg_keys_dir"
aws s3 cp --region=us-west-2 --recursive s3://encoded-conf-prod/pg-aws-keys "$pg_keys_dir"
if [ ! -f "$pg_keys_dir/credentials" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ubuntu home pg aws creds"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi

## Copy postgres aws to home
pg_keys_dir='/home/ubuntu/pg-aws-keys'
if [ ! -f "$pg_keys_dir/credentials" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: ubuntu home pg aws creds"
    # Build has failed
    touch "$encd_failed_flag"
    exit 1
fi
sudo -u root mkdir /var/lib/postgresql/.aws
sudo -u root cp /home/ubuntu/pg-aws-keys/* ~postgres/.aws/
sudo -u root chown -R postgres:postgres /var/lib/postgresql/.aws/

# Add ssh keys to postgres user
sudo -u postgres mkdir /var/lib/postgresql/.ssh
sudo -u root cp /home/ubuntu/.ssh/authorized_keys /var/lib/postgresql/.ssh/authorized_keys
sudo -u root chown -R postgres:postgres /var/lib/postgresql/.ssh/

echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Setup postgres configuration"
## Copy pg confs from encoded repo to pg conf dir
for filename in 'custom.conf' 'demo.conf' 'master.conf' 'recovery.conf'; do
    copy_with_permission "$PG_CONF_SRC" "$PG_CONF_DEST" "$filename"
done

append_with_user "$ENCD_WALE_S3_PREFIX" 'postgres' "$PG_CONF_DEST/WALE_S3_PREFIX"

## pg conf master.conf:
# Create the archive_command variable with agrument and store as string
#
# 'In archive_command, %p is replaced by the path name of the file to archive,
#  while %f is replaced by only the file name'
# -https://www.postgresql.org/docs/11/continuous-archiving.html
#
wale_push_cmd="archive_command = '\
$WALE_BIN/envdir $WALE_ENV \
$WALE_BIN/wal-e \
wal-push \"%p\"\
'"

if [ "$ENCD_ROLE" == 'candidate' ]; then
    # Only production needs wal-e push ability? Move to ENCD_ROLE='candidate'?"
    append_with_user "$wale_push_cmd" 'postgres' "$PG_CONF_DEST/master.conf"
fi

## pg conf recovery.conf
wale_fetch_cmd="restore_command = '\
$WALE_BIN/envdir $WALE_ENV \
$WALE_BIN/wal-e \
wal-fetch \"%f\" \"%p\"\
'"

standby_mode_cmd="standby_mode = $standby_mode"
append_with_user "$wale_fetch_cmd" 'postgres' "$PG_CONF_DEST/recovery.conf"
append_with_user "$standby_mode_cmd" 'postgres' "$PG_CONF_DEST/recovery.conf"
# Set db to recovery mode
sudo -u postgres ln -s "$PG_CONF_DEST/recovery.conf" "$PG_DATA/"

## pg conf postgresql.conf
include_custom="include 'custom.conf'"
append_with_user "$include_custom" 'postgres' "$PG_CONF_DEST/postgresql.conf"
if [ ! "$ENCD_ROLE" == 'candidate' ]; then
  include_demo="include 'demo.conf'"
  append_with_user "$include_demo" 'postgres' "$PG_CONF_DEST/postgresql.conf"
fi


### Create db
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Create encode db"
sudo -u postgres createuser encoded
sudo -u postgres createdb --owner=encoded encoded


### Wale-E
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Install wal-e"
## Create Wal-e ENV - python3 only
sudo -u root mkdir -p "$WALE_ENV"
sudo -u root chown postgres:postgres "$WALE_ENV"
for filename in 'AWS_ACCESS_KEY_ID' 'AWS_SECRET_ACCESS_KEY' 'AWS_REGION'; do
    copy_with_permission "$AWS_CREDS_DIR" "$WALE_ENV" "$filename"
done
copy_with_permission "$PG_CONF_DEST" "$WALE_ENV" 'WALE_S3_PREFIX'

## Install wal-e
sudo -u root mkdir -p "$WALE_DIR"
sudo -u root chown postgres:postgres "$WALE_DIR"
sudo -u root cp "$WALE_REQS_SRC" "$WALE_REQS_DST"
sudo -u root chown postgres:postgres "$WALE_REQS_DST"
sudo -H -u postgres "$ENCD_PY3_PATH" -m venv "$WALE_VENV"
if [ ! -f "$WALE_BIN/pip" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: Wale bin does not exist"
    touch "$encd_failed_flag"
    exit 1
fi
sudo -H -u postgres "$WALE_BIN/pip" install pip setuptools --upgrade
sudo -H -u postgres "$WALE_BIN/pip" install wheel
sudo -H -u postgres "$WALE_BIN/pip" install -r "$WALE_REQS_DST"
sudo -u postgres git clone --branch v1.1.1 https://github.com/wal-e/wal-e.git "$WALE_DIR/wal-e"
sudo -H -u postgres "$WALE_BIN/pip" install -e "$WALE_DIR/wal-e"

### Postgres
echo -e "\n\t$APP_WRAPPER$ENCD_INSTALL_TAG $(basename $0) Do initial wal-e backup-fetch"
## Update db from wale backup
sudo -u postgres pg_ctlcluster 11 main stop
sudo -u postgres "$WALE_BIN/envdir" "$WALE_ENV" "$WALE_BIN/wal-e" backup-fetch "$PG_DATA" LATEST

## Restart
if [ "$ENCD_PG_OPEN" == 'true' ]; then
    append_with_user "listen_addresses='*'" 'postgres' "$PG_CONF_DEST/postgresql.conf"
    append_with_user "host all all 0.0.0.0/0 trust" 'postgres' "$PG_CONF_DEST/pg_hba.conf"
fi
sudo -u postgres pg_ctlcluster 11 main start

## Wait for psql to come up
$ENCD_SCRIPTS_DIR/app-pg-status.sh
if [ -f "$encd_failed_flag" ]; then
    echo -e "\n\t$ENCD_INSTALL_TAG $(basename $0) ENCD FAILED: App pg status"
    exit 1
fi
