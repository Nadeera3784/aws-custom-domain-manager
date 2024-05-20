import pytz
import json
import boto3

def lambda_handler(event: None, context: None):
    return main_method(event['number'])

def main_method(value: None):
    return {
        "statusCode": 200,
        "message": value+1
    }

def some_aws_method(event, context):
    # Retrieve the list of existing buckets
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    buckets = []

    # Output the bucket names
    print('Existing buckets:')
    for bucket in response['Buckets']:
        buckets.append(bucket["Name"])

    return {
        'statusCode': 200,
        'buckets': buckets
    }