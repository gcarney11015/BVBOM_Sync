import boto3
import copy
import json
import os


def list_value(field, obj):
    if not field in obj:
        return None
    value = obj[field]
    if not isinstance(value, list):
        return None
    return value


def single_value(field, obj):
    if not field in obj:
        return None
    value = obj[field]
    if not isinstance(value, list):
        return value
    if len(value) == 0:
        return None
    return value[0]


def hitFieldsToAddFields(hitFields):
    values = {
        'activity_date': single_value('activity_date', hitFields),
        'activity_type': single_value('activity_type', hitFields),
        'associated_items': list_value('associated_items', hitFields),
        'content': single_value('content', hitFields),
        'content_encoding': single_value('content_encoding', hitFields),
        'content_type': single_value('content_type', hitFields),
        'date_indexed': single_value('date_indexed', hitFields),
        'description': single_value('description', hitFields),
        'discipline': single_value('discipline', hitFields),
        'discipline_literal': single_value('discipline', hitFields),        
        'keywords': list_value('keywords', hitFields),
        'keywords_literal': list_value('keywords', hitFields),
        'links': list_value('links', hitFields),
        'project_name': single_value('project_name', hitFields),
        'project_name_literal': single_value('project_name', hitFields),
        'project_number': single_value('project_number', hitFields),
        'resourcename': single_value('resourcename', hitFields),
        'source': single_value('source', hitFields),
        'source_literal': single_value('source', hitFields),
        'title': single_value('title', hitFields),
    }

    result = {}

    for k, v in values.items():
        if not v is None:
            result[k] = v

    return result


def hitToAdd(hit):
    result = {
        'fields': hitFieldsToAddFields(hit['fields']),
        'id': hit['id'],
        'type': 'add',
    }
    return result


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


def getCloudSearchDomain(name):
    cloudSearchClient = boto3.client('cloudsearch')
    domains = cloudSearchClient.describe_domains(DomainNames=[name])
    domainStatusList = domains['DomainStatusList']
    if len(domainStatusList) == 1:
        return domainStatusList[0]
    else:
        return None


def uploadDocuments(path):
    domain = getCloudSearchDomain('mat-tracking')
    # print(json.dumps(domain, indent=2))
    endpoint = domain['DocService']['Endpoint']
    client = boto3.client('cloudsearchdomain', endpoint_url='https://' + endpoint)

    files = [os.path.join(path, f) for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.endswith('.json')]
    files.sort()

    for file in files:
        with open(file, 'rb') as f:
            print(file, end='')
            response = client.upload_documents(
                documents=f,
                contentType='application/json'
            )
            print(f" a: {response['adds']}, d: {response['deletes']}")
        f.closed


def generateAddsAndDeletes():
    domain = getCloudSearchDomain('bvmm04')
    searchEndpoint = domain['SearchService']['Endpoint']

    cloudSearchDomainClient = boto3.client('cloudsearchdomain',
                                           endpoint_url='https://' + searchEndpoint)

    BatchSize = 250
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


# generateAddsAndDeletes()
uploadDocuments('./add')
