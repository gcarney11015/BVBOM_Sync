import boto3
import io
import json
import os
import sys

from .download import hitToSearch


def hitsToFilenameAndStream(hits):
    if len(hits) == 0:
        return None

    filename = hits[0]['id'] + '.json'

    searches = map(hitToSearch, hits)
    searchStrings = map(json.dumps, searches)

    data = '\n'.join(searchStrings).encode('utf-8')

    stream = io.BytesIO(data)
    return (filename, stream)

def listToGroups(list, itemsPerGroup):
    result = []
    start = 0
    while start < len(list):
        sublist = list[start: start + itemsPerGroup]
        result.append(sublist)
        start += itemsPerGroup

    return result


def synchronize(searchUrl, searchSize, recordsPerFile, bucketName, folderName):
    client = boto3.client('cloudsearchdomain',
                          endpoint_url=searchUrl)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketName)

    cursor = 'initial'
    filesUploaded = 0
    recordsProcessed = 0

    while True:
        response = client.search(cursor=cursor,
            partial=False,
            query='matchall',
            queryParser='structured',
            size=searchSize,
            sort='_id asc')

        hits = response['hits']['hit']

        if len(hits) == 0:
            break

        groups = listToGroups(hits, recordsPerFile)
        for group in groups:
            fAndS = hitsToFilenameAndStream(group)
            key = folderName + '/' + fAndS[0]
            data = fAndS[1]
            bucket.upload_fileobj(data, key)
            print('Uploaded: {0}, {1} records'.format(key, len(group)))
            filesUploaded += 1
            recordsProcessed += len(group)

        if len(hits) < searchSize:
            break

        cursor = response['hits']['cursor']
        
    print('Processed {0} records in {1} files.'.format(recordsProcessed, filesUploaded))


if __name__ == '__main__':
    searchUrl = os.environ['SYNC_CLOUDSEARCH_URL']
    searchSize = int(os.environ['SYNC_SEARCH_SIZE'])
    recordsPerFile = int(os.environ['SYNC_RECORDS_PER_FILE'])
    bucketName = os.environ['SYNC_S3_BUCKET_NAME']
    folderName = os.environ['SYNC_S3_FOLDER_NAME']

    synchronize(searchUrl, searchSize, recordsPerFile, bucketName, folderName)
