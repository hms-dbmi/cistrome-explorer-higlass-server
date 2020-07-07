#!/usr/bin/env bash

. /opt/conda/etc/profile.d/conda.sh
conda activate higlass-server

mkdir -p /data/log

echo "Mounting httpfs"
mkdir -p $HTTPFS_HTTP_DIR
mkdir -p $HTTPFS_HTTPS_DIR

simple-httpfs $HTTPFS_HTTPS_DIR --lru-capacity 1000 --disk-cache-dir /data/disk-cache --disk-cache-size 4294967296
simple-httpfs $HTTPFS_HTTP_DIR --lru-capacity 1000 --disk-cache-dir /data/disk-cache --disk-cache-size 4294967296

echo "Mounting goofys"
mkdir -p $GOOFYS_DIR

# Reference: https://github.com/kahing/goofys#usage
/software/goofys $S3_BUCKET_HGS $GOOFYS_DIR 

python manage.py migrate

# /data is a mounted volume, so the Dockerfile can not create subdirectories.
# If this is re-run, the loaddata will fail, which right now is a feature.
python manage.py loaddata default-viewconf-fixture.xml
uwsgi --ini /higlass-server/uwsgi.ini --socket :8001 --module higlass_server.wsgi --workers $WORKERS