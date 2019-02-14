## Overview

This project synchronizes the Athena S3 data lake with the contents of the CloudSearch domain. `synchronize.sh` does:

1. Removes all content from the S3 bucket/folder.
2. Invokes the `pkg.synchronize.py` module to query CloudSearch, transform the data, then upload it to S3 that feeds Athena.

This functionality is Docker-ized to support building a container that can run the logic in any container hosting environment.

## Python Environment

The project uses Python 3.7.x. It is recommended to use virtual environments to ensure correct interpreter versions and dependencies. The virtual environment should be activated whenever Python-related activities are performed (i.e. running apps, installing packages, etc.).

1. Create a Python 3.7.x virtual environmet: `python3 -m venv venv`
2. Activate the virtual environment: `source ./venv/bin/activate`. `python --version` should report Python 3.7.x.
3. Install required packages: `pip install -r requirements.txt`

## Run the Synchronization Process

AWS credentials must be available, for example in `~/.aws/credentials`. See the [boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) for details.

1. Set environment variables. See `set-environment` file for sample settings:
  * SYNC_CLOUDSEARCH_URL - URL of the CloudSearch domain search endpoint.
  * SYNC_SEARCH_SIZE - Size of individual CloudSearch search requests.
  * SYNC_RECORDS_PER_FILE - Maximum number of CloudSearch documents uploaded to S3 files.
  * SYNC_S3_BUCKET_NAME - S3 bucket name.
  * SYNC_S3_FOLDER_NAME - S3 folder name within the bucket.
2. `python -m pkg.synchronize`

## Build the Docker Image and Push to AWS

These steps are pulled from Amazon Container Services/Repositories.

1. `$(aws ecr get-login --no-include-email --region us-east-1)`
2. `docker build -t mat-tracking/cloudsearch-to-athena .`
3. `docker tag mat-tracking/cloudsearch-to-athena:latest 687040445886.dkr.ecr.us-east-1.amazonaws.com/mat-tracking/cloudsearch-to-athena:latest`
4. `docker push 687040445886.dkr.ecr.us-east-1.amazonaws.com/mat-tracking/cloudsearch-to-athena:latest`
