#!/bin/bash

aws s3 rm s3://${SYNC_S3_BUCKET_NAME}/${SYNC_S3_FOLDER_NAME} --recursive --exclude "TemplateItem-inventory.json"
python -m pkg.synchronize
