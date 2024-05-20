#!/usr/bin/env python3
import boto3
import time
import json
"""
AWS region set for us-east-1 as this ACM certificate is used by Cloudfront
"""
client = boto3.client('acm', 'us-east-1')


def obtain_certs(domain, application):
    """ Request ACM certificates for the provided domain, the app parameter is used to tag the AWS resource.
    Parameters
    ----------
    domain : string (Domain used for ACM certificate)
    app: string (Application that requested the certificate)
    Returns
    -------
    ACM certificate ARN: string
    """    

    response = client.request_certificate(
    DomainName=domain,
    ValidationMethod='DNS',
    SubjectAlternativeNames=[f'*.{domain}'],
    IdempotencyToken='string',
    Tags=[
        {
            'Key': 'requester',
            'Value': application
        },
    ]
    )

    return response

def describe_certificate(certificate_arn):
    """ Once the ACM certificate is obtained, the respective ARN is used to obtain the CNAME record used to prove domain ownership.
    Parameters
    ----------
    certificate_arn : string (ACM certificate created previously)
    Returns
    -------
    CNAME record for ownership challenge
    """        

    response = client.describe_certificate(
    CertificateArn=certificate_arn
    )
    print(response)
    return response  

    

def lambda_handler(event, context):
    payload = json.loads(event['body'])
    try:
        domain = payload['domain']
        application    = payload['application']
    except Exception as e:
        print(e)

    certificate_arn = obtain_certs(domain, application)
    # Sleep necessary as to wait the ACM certificate arn to be created
    time.sleep(10)
    
    if certificate_arn != None:
    
        certificate_details = describe_certificate(certificate_arn["CertificateArn"])
        cname_record = certificate_details["Certificate"]["DomainValidationOptions"][1]["ResourceRecord"]
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(cname_record)
        }
    else:
        return {
            "statusCode": 502,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": "ACM certificate could not be obtained."
        }

   

