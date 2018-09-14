
import json
import boto3
import os
from botocore.exceptions import ClientError


table_name = os.environ['DYNAMODB_TABLE_NAME']
topic = os.environ['OUTPUT_TOPIC_ARN']
codecommit = boto3.client('codecommit')
dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')

MAX_COMMITS = 20
MAX_DEPTH = 500


def handler(event, context):
    for record in event['Records']:

        repository = record['eventSourceARN'].split(':')[5]
        region = record['eventSourceARN'].split(':')[3]
        repository_id = '%s:%s' % (repository, region)
        before = previous(repository_id)

        for reference in record['codecommit']['references']:

            head = reference['commit']
            ref = reference['ref']

            update(repository_id, before, head)

            if before is None:
                before = head

            payload = {
                'ref': ref,
                'head': head,
                'size': 0,
                'before': before,
                'commits': [],
            }

            commits(repository, region, before, payload, head)

            sns.publish(TopicArn=topic, Message=json.dumps(payload))

    return repository_id


def commits(repository, region, before, payload, commit_id):
    """Recursively walk through the commits"""
    if payload['size'] >= MAX_DEPTH:
        return

    if commit_id == before:
        return

    commit = codecommit.get_commit(repositoryName=repository, commitId=commit_id)

    commit['link'] = 'https://console.aws.amazon.com/codecommit/home?region=%s#/repository/%s/commit/%s' % (region, repository, commit_id)

    append(payload, commit)

    if 'parents' not in commit['commit'] or commit['commit']['parents'] is None or len(commit['commit']['parents']) is 0:
        return

    for parent in commit['commit']['parents']:
        if parent == before:
            return
        commits(repository, region, before, payload, parent)


def append(payload, commit):
    """Append up the max commits and increase the size/count"""
    payload['size'] = payload['size'] + 1

    if len(payload['commits']) <= MAX_COMMITS:
        payload['commits'].append(commit)


def previous(repository_id):
    """Returns the previous commit id or none"""
    response = dynamodb.get_item(TableName=table_name, ConsistentRead=True, Key={ 'repository_id': { 'S': repository_id } })

    # If the response is empty, we need to create a new one starting here
    if 'Item' in response:
        return response['Item']['head']['S']

    return None


def update(repository_id, before, head):
    """Upsert the database with the current id"""
    if before is None:
        response = dynamodb.put_item(TableName=table_name, Item={ 'repository_id': { 'S': repository_id }, 'head': { 'S': head } })
        return

    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key={ 'repository_id': { 'S': repository_id } },
            UpdateExpression='SET head = :head',
            ConditionExpression='head = :before',
            ExpressionAttributeValues = {
                ':head': { 'S': head },
                ':before': { 'S': before }
            }
        )

    except ClientError as e:
        if not e.response['Error']['Code'] == "ConditionalCheckFailedException":
            raise e


