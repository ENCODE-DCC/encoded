#!/bin/bash
# Setup postgres 9.3 or 11,
#   install wal-e,
#   run backup fetch
# postgres user
# apt deps:
#   postgresql-9.3 or 11
#   python2.7-dev 3.4 # wal-e
#   lzop # wal-e
echo -e "\n**** ENCDINSTALL $(basename $0) ****"

### Arguments
standby_mode="$1"
ROLE="$2"
WALE_S3_PREFIX="$3"
PG_VERSION="$4"
python_version=0
if [ "$PG_VERSION" == '9.3' ]; then
    python_version=2
fi
if [ "$PG_VERSION" == '11' ]; then
    echo '****************python3*******************'
    python_version=3
fi
if [ $python_version -eq 0 ]; then
    echo 'INSTALL FAILURE(pg-install.sh): Postgres version $PG_VERSION is unknown'
    exit 1
fi
pg_version="$(echo $PG_VERSION | sed 's/\.//g')"


### Variables
AWS_CREDS_DIR='/var/lib/postgresql/.aws'
AWS_PROFILE='default'

PG_CONF_DEST="/etc/postgresql/$PG_VERSION/main"
PG_CONF_SRC="home/ubuntu/encoded/cloud-config/deploy-run-scripts/conf-pg$pg_version"
PG_DATA="/var/lib/postgresql/$PG_VERSION/main"

WALE_DIR='/opt/wal-e'
WALE_VENV="$WALE_DIR"
WALE_BIN="$WALE_VENV/bin"
WALE_ENV=
WALE_REQS='/home/ubuntu/encoded/wal-e-requirements.txt'
if [ $python_version -eq 3 ]; then
    WALE_DIR='/opt/pg-wal-e'
    WALE_VENV="$WALE_DIR/.py343-wal-e"
    WALE_BIN="$WALE_VENV/bin"
    WALE_ENV='/etc/wal-e.d/env'
    WALE_REQS='/home/ubuntu/encoded/wal-e-requirements-py3.txt'
fi


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

## Copy postgres aws to home
sudo -u root mkdir /var/lib/postgresql/.aws
sudo -u root cp /home/ubuntu/pg-aws-keys/* ~postgres/.aws/
sudo -u root chown -R postgres:postgres /var/lib/postgresql/.aws/

## Copy pg confs from encoded repo to pg conf dir
for filename in 'custom.conf' 'demo.conf' 'master.conf' 'recovery.conf'; do
    copy_with_permission "$PG_CONF_SRC" "$PG_CONF_DEST" "$filename"
done

## pg conf WALE_S3_PREFIX(Input arg 3)
# This will be copied to WALE_ENV too
if [ $python_version -eq 3 ]; then
    append_with_user "$WALE_S3_PREFIX" 'postgres' "$PG_CONF_DEST/WALE_S3_PREFIX"
else
    # Lower case wal-e prefix file is not standard
    append_with_user "$WALE_S3_PREFIX" 'root' "$PG_CONF_DEST/wale_s3_prefix"
fi

## pg conf master.conf:
# Create the archive_command variable with agrument and store as string
#
# 'In archive_command, %p is replaced by the path name of the file to archive,
#  while %f is replaced by only the file name'
# -https://www.postgresql.org/docs/11/continuous-archiving.html
#
# Python 2 archive_command
# 1. Where wal-e gets AWS credentials
# 2. The wal-e command with AWS s3 prefix
# 3. The wal-e push sub command argument %p
##
wale_push_cmd="archive_command = '\
$WALE_BIN/envfile --config $AWS_CREDS_DIR/credentials --section $AWS_PROFILE --upper -- \
$WALE_BIN/wal-e --s3-prefix=$WALE_S3_PREFIX \
wal-push \"%p\"\
'"
## Python 3 archive_command
# 1. Where wal-e gets AWS credentials
# 2. The wal-e command with AWS s3 prefix
# 3. The wal-e push sub command argument %p
##
wale_push_cmd_py3="archive_command = '\
$WALE_BIN/envdir $WALE_ENV \
$WALE_BIN/wal-e \
wal-push \"%p\"\
'"
if [ $python_version -eq 3 ]; then
    wale_push_cmd="$wale_push_cmd_py3"
fi
if [ "$ROLE" == 'candidate' ]; then
    # Only production needs wal-e push ability? Move to ROLE='candidate'?"
    append_with_user "$wale_push_cmd" 'postgres' "$PG_CONF_DEST/master.conf"
fi

## pg conf recovery.conf
wale_fetch_cmd="restore_command = '\
$WALE_BIN/wal-e --aws-instance-profile --s3-prefix=$WALE_S3_PREFIX \
wal-fetch \"%f\" \"%p\"\
'"
wale_fetch_cmd_py3="restore_command = '\
$WALE_BIN/envdir $WALE_ENV \
$WALE_BIN/wal-e \
wal-fetch \"%f\" \"%p\"\
'"
if [ $python_version -eq 3 ]; then
    wale_fetch_cmd="$wale_fetch_cmd_py3"
fi
standby_mode_cmd="standby_mode = $standby_mode"
append_with_user "$wale_fetch_cmd" 'postgres' "$PG_CONF_DEST/recovery.conf"
append_with_user "$standby_mode_cmd" 'postgres' "$PG_CONF_DEST/recovery.conf"
# Set db to recovery mode
sudo -u postgres ln -s "$PG_CONF_DEST/recovery.conf" "$PG_DATA/"

## pg conf postgresql.conf
include_custom="include 'custom.conf'"
append_with_user "$include_custom" 'postgres' "$PG_CONF_DEST/postgresql.conf"
if [ ! "$ROLE" == 'candidate' ]; then
  include_demo="include 'demo.conf'"
  append_with_user "$include_demo" 'postgres' "$PG_CONF_DEST/postgresql.conf"
fi


### Create db
sudo -u postgres createuser encoded
sudo -u postgres createdb --owner=encoded encoded


### Wale-E
## Create Wal-e ENV - python3 only
if [ $python_version -eq 3 ]; then
    sudo -u root mkdir -p "$WALE_ENV"
    sudo -u root chown postgres:postgres "$WALE_ENV"
    for filename in 'AWS_ACCESS_KEY_ID' 'AWS_SECRET_ACCESS_KEY' 'AWS_REGION'; do
        copy_with_permission "$AWS_CREDS_DIR" "$WALE_ENV" "$filename"
    done
    copy_with_permission "$PG_CONF_DEST" "$WALE_ENV" 'WALE_S3_PREFIX'
fi
## Install wal-e
if [ $python_version -eq 3 ]; then
    sudo -u root mkdir -p "$WALE_DIR"
    sudo -u root chown postgres:postgres "$WALE_DIR"
    sudo -u root cp "$WALE_REQS" "$WALE_DIR/wal-e-requirements.txt"
    sudo -u root chown postgres:postgres "$WALE_DIR/wal-e-requirements.txt"
    sudo -H -u postgres python3 -m venv "$WALE_VENV"
    sudo -H -u postgres "$WALE_BIN/pip" install pip setuptools==43 boto awscli --upgrade
    sudo -H -u postgres "$WALE_BIN/pip" install -r "$WALE_DIR/wal-e-requirements.txt"
    sudo -u postgres git clone https://github.com/wal-e/wal-e.git "$WALE_DIR/wal-e"
    sudo -H -u postgres "$WALE_BIN/pip" install -e "$WALE_DIR/wal-e"
else
    sudo -u root mkdir "$WALE_DIR"
    sudo -u root chown postgres:postgres "$WALE_DIR"
    cd "$WALE_DIR"
    cp $WALE_REQS ./wal-e-requirements.txt
    sudo -u postgres virtualenv --python=python2.7 ./
    sudo -u postgres "$WALE_BIN/pip" install -r ./wal-e-requirements.txt
fi

### Postgres
## Update db from wale backup
if [ $python_version -eq 3 ]; then
    sudo -u postgres pg_ctlcluster 11 main stop
    sudo -u postgres "$WALE_BIN/envdir" "$WALE_ENV" "$WALE_BIN/wal-e" backup-fetch "$PG_DATA" LATEST
    #DEBUG Helper sudo -u postgres /opt/pg-wal-e/.py343-wal-e/bin/envdir /etc/wal-e.d/env /opt/pg-wal-e/.py343-wal-e/bin/wal-e backup-fetch /var/lib/postgresql/11/main LATEST
else
    sudo -u postgres /etc/init.d/postgresql stop
    sudo -u postgres "$WALE_BIN/wal-e" --aws-instance-profile --s3-prefix="$WALE_S3_PREFIX" backup-fetch "$PG_DATA" LATEST
fi
## Restart
if [ $python_version -eq 3 ]; then
    sudo -u postgres pg_ctlcluster 11 main start
else
    sudo -u postgres /etc/init.d/postgresql start
fi
## Wait for it to come up
psql_cnt=0
until sudo -u postgres psql postgres -c ""; do
    psql_cnt=$((psql_cnt+1))
    sleep 10;
    if [ $psql_cnt -gt 10 ]; then
        echo 'INSTALL FAILURE(pg-install.sh): Postgres did not restart'
        exit 123
    fi
done
