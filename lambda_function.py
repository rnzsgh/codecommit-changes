
import json
import boto3
import os
import time
import sys
from botocore.exceptions import ClientError

topic = os.environ['OUTPUT_TOPIC_ARN']
codecommit = boto3.client('codecommit')
sns = boto3.client('sns')

MAX_COMMITS = 20

sys.setrecursionlimit(5000)

def handler(event, context):
    """Handler function for the Lambda"""

    seen = set()

    region = event['region']

    head = event['detail']['commitId']
    before = event['detail']['oldCommitId']

    ref = event['detail']['referenceFullName']
    branch = event['detail']['referenceName']
    repo = event['detail']['repositoryName']

    payload = { 'ref': ref, 'head': head, 'size': 0, 'before': before, 'commits': [] }

    commits(repo, region, seen, before, payload, head)

    sns.publish(TopicArn=topic, Message=json.dumps(payload))

    return ref


def commits(repo, region, seen, before, payload, commit_id):
    """Recursively walk through the commits"""
    if commit_id in seen or commit_id == before:
        return

    seen.add(commit_id)

    commit = None
    while True:
        try:
            commit = codecommit.get_commit(repositoryName=repo, commitId=commit_id)
            break
        except ClientError as err:
            if err.response['Error']['Code'] != 'ThrottlingException':
                raise err
            time.sleep(1)

    commit.pop('ResponseMetadata', None)
    commit['commit']['link'] = 'https://console.aws.amazon.com/codecommit/home?region=%s#/repository/%s/commit/%s' % (region, repo, commit_id)

    append(payload, commit)

    if 'parents' in commit['commit'] and commit['commit']['parents'] is not None:
        for parent in commit['commit']['parents']:
            if parent == before:
                return
            commits(repo, region, seen, before, payload, parent)


def append(payload, commit):
    """Append up the max commits and increase the size/count"""
    payload['size'] += 1

    if len(payload['commits']) <= MAX_COMMITS:
        payload['commits'].append(commit['commit'])



