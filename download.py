import boto3
import copy
import json


def fieldToLiteral(field):
    literal = copy.deepcopy(field)


def hitToAdd(hit):
    add = copy.deepcopy(hit)
    add['type'] = 'add'

    hitFields = hit['fields']

    for sourceName in ['discipline', 'keywords', 'project_name', 'source']:
        if sourceName in hitFields:
            sourceValue = hitFields[sourceName]
            add['fields'][sourceName + '_literal'] = copy.deepcopy(sourceValue)

    return add


def hitToDelete(hit):
    result = {
        'id': hit['id'],
        'type': 'delete',
    }
    return result


def search(client, cursor, size):
    response = client.search(
        cursor=cursor,
        partial=False,
        query='matchall',
        queryParser='structured',
        size=size,
    )
    return response


def generateAddsAndDeletes():
    cloudSearchClient = boto3.client('cloudsearch')
    domains = cloudSearchClient.describe_domains(DomainNames=['bvmm04'])

    # print(json.dumps(domains, indent=2))

    searchEndpoint = domains['DomainStatusList'][0]['SearchService']['Endpoint']

    cloudSearchDomainClient = boto3.client('cloudsearchdomain',
                                           endpoint_url='https://' + searchEndpoint)

    BatchSize = 500
    cursor = 'initial'

    while True:
        response = search(cloudSearchDomainClient, cursor, BatchSize)
        # print(json.dumps(response, indent=2))

        hitList = response['hits']['hit']

        if len(hitList) == 0:
            break

        startIndex = response['hits']['start']
        print(f'{startIndex}')
        paddedStartIndex = f'{startIndex:06}'

        with open('./add/' + paddedStartIndex + '.json', 'w') as f:
            adds = [hitToAdd(hit) for hit in hitList]
            f.write(json.dumps(adds))
        f.closed

        with open('./delete/' + paddedStartIndex + '.json', 'w') as f:
            deletes = [hitToDelete(hit) for hit in hitList]
            f.write(json.dumps(deletes))
        f.closed

        if len(hitList) < BatchSize:
            break

        cursor = response['hits']['cursor']


generateAddsAndDeletes()
