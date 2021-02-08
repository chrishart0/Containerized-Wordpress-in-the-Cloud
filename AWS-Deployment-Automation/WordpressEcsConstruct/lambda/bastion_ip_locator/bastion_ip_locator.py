import json
import os
import boto3
from botocore.exceptions import ClientError

client = boto3.client('ecs')

def handler(event, context):
    print('request: {}'.format(json.dumps(event)))

    #Set scope for IP variable
    ip = ''
    
    #Get list of tasks from our service
    response = client.list_tasks(
        cluster=os.environ['CLUSTER_NAME'],
        serviceName=os.environ['SERVICE_NAME']
    )
        
    #Extract task ARN
    taskArn = response['taskArns'][0]
    print(taskArn)
        
    #User Task ARN to get task details
    response = client.describe_tasks(
        cluster=os.environ['CLUSTER_NAME'],
        tasks=[
            taskArn
        ]
    )
       
    #Extract IP from task details
    for item in response['tasks'][0]['attachments'][0]['details']:
        if item['name'] == 'privateIPv4Address':
            ip = item['value']
    
    
    return {
        "statusCode": 200,
        "body": json.dumps({
            "ip": ip
        }),
    }