import boto3
import io
import json
import os
import rx
from rx import AnonymousObservable, Observable
import sys

from .download import hitToSearch


class CloudSearchDomainRx(AnonymousObservable):

    def __init__(self, client, **searchArgs):

        def subscribe(observer):
            try:
                response = client.search(**searchArgs)
            except:
                observer.on_error(sys.exc_info()[1])
                return

            observer.on_next(response)
            observer.on_completed()

        super(CloudSearchDomainRx, self).__init__(subscribe)


class BucketUploadRx(AnonymousObservable):

    def __init__(self, bucket, key, data):

        def subscribe(observer):
            try:
                bucket.upload_fileobj(data, key)
            except:
                observer.on_error(sys.exc_info()[1])
                return

            observer.on_completed()

        super(BucketUploadRx, self).__init__(subscribe)

def hitsToFilenameAndStream(hits):
    if len(hits) == 0:
        return ('none.json', io.BytesIO(None))

    filename = hits[0]['id'] + '.json'

    searches = map(hitToSearch, hits)
    searchStrings = map(json.dumps, searches)

    data = '\n'.join(searchStrings).encode('utf-8')

    stream = io.BytesIO(data)
    return (filename, stream)


def synchronize(searchUrl, searchSize, recordsPerFile, bucketName, keyPrefix):
    def hitsToGroups(hits):
        result = []
        start = 0
        while start < len(hits):
            sublist = hits[start: start + recordsPerFile]
            result.append(sublist)
            start += recordsPerFile

        return result

    def toUpload(bucket, key, stream):
        return BucketUploadRx(bucket, key, stream) \
            .do_action(on_completed = lambda: print('Uploaded: ' + key) )

    client = boto3.client('cloudsearchdomain',
                          endpoint_url=searchUrl)

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucketName)

    cursor = 'initial'

    while True:
        try:
            response = client.search(cursor=cursor,
                                     partial=False,
                                     query='matchall',
                                     queryParser='structured',
                                     size=searchSize,
                                     sort='_id asc')
        except:
            print("Error Occurred: {0}".format(sys.exc_info()[1]))
            break

        hits = response['hits']['hit']

        Observable.of(hits) \
            .map(hitsToGroups) \
            .select_many(lambda it: Observable.from_(it)) \
            .map(hitsToFilenameAndStream) \
            .select_many(lambda it: toUpload(bucket, keyPrefix + it[0], it[1])) \
            .subscribe(on_next=lambda value: print('Received: {0}'.format(value)),
                       on_error=lambda error: print('Error Occurred: {0}'.format(error))
        )

        if len(hits) < searchSize:
            break

        cursor=response['hits']['cursor']


if __name__ == '__main__':
    searchUrl = os.environ['SYNC_CLOUDSEARCH_URL']
    searchSize = int(os.environ['SYNC_SEARCH_SIZE'])
    recordsPerFile = int(os.environ['SYNC_RECORDS_PER_FILE'])
    bucketName = os.environ['SYNC_S3_BUCKET_NAME']
    keyPrefix = os.environ['SYNC_S3_KEY_PREFIX']

    synchronize(searchUrl, searchSize, recordsPerFile, bucketName, keyPrefix)
