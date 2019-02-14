#!/bin/bash

docker run \
    --env SYNC_CLOUDSEARCH_URL='https://search-mat-tracking-eou435pggpmnyzh7pjnxfskpga.us-east-1.cloudsearch.amazonaws.com' \
    --env SYNC_RECORDS_PER_FILE='1000' \
    --env SYNC_S3_BUCKET_NAME='mat-tracking-item-db-backup' \
    --env SYNC_S3_FOLDER_NAME='foo' \
    --env SYNC_SEARCH_SIZE='2000' \
    --env AWS_ACCESS_KEY_ID='XXX' \
    --env AWS_DEFAULT_REGION='us-east-1' \
    --env AWS_SECRET_ACCESS_KEY='YYY' \
    mat-tracking/cloudsearch-to-athena:latest

# command to execute shall on image
# docker run -it mat-tracking/cloudsearch-to-athena:latest /bin/bash
