import json
import os
import boto3
from botocore.exceptions import ClientError

secrets_client = boto3.client('secretsmanager')


def handler(event, context):
    print('request: {}'.format(json.dumps(event)))

    body = resp['Payload'].read()

    print('downstream response: {}'.format(body))
    return json.loads(body)