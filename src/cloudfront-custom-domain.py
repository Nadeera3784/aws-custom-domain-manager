#!/usr/bin/env python3
import boto3
import json



def get_certificate_arn(domain):
    """ Obtain the certificate arn is the matches with the provided domain and is ISSUED
    Parameters
    ----------
    domain : string (Domain used to create the ACM certificate)
    Returns
    -------
    ACM certificate ARN: string
    """     
    client = boto3.client('acm', 'us-east-1')
    response = client.list_certificates(
      CertificateStatuses=[
          'ISSUED'
      ]
    )
    for value in response['CertificateSummaryList']:
        if value['DomainName'] == domain:
            return value['CertificateArn']

    return False
    
def create_cloudfront(url, certificate_arn, origin, application):
    """ Obtain the certificate arn is the matches with the provided domain and is ISSUED
    Parameters
    ----------
    url : string (URL used by custom domain, used to create Cloudfront)
    certificate_arn : string (Returned by get_certificate_arn(), used to assign certificate to Cloudfront)
    origin : string (Origin for content  used by Cloudfront, usually a Application Load Balancer URL)
    application : string (Application that created custom domain)
    Returns
    -------
    Cloudfront details: dict
    """   

    client = boto3.client('cloudfront')

    response = client.create_distribution(
        DistributionConfig={
            'CallerReference': url,
            'Aliases': {
                'Quantity': 1,
                'Items': [
                    url,
                ]
            },
            'DefaultRootObject': '',
            'Origins': {
                'Quantity': 1,
                'Items': [
                    {
                        'Id': url,
                        'DomainName': origin,
                        'CustomOriginConfig': {
                            'HTTPPort': 80,
                            'HTTPSPort': 443,
                            'OriginProtocolPolicy': 'https-only'
                        },
                    },
                ]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': url,
                'ViewerProtocolPolicy': 'redirect-to-https',
                'AllowedMethods': {
                    'Quantity': 7,
                    'Items': [
                        'GET','HEAD','POST','PUT','PATCH','OPTIONS','DELETE',
                    ],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': [
                            'HEAD', 'GET',
                        ]
                    }
                },
                'MinTTL': 0,
                'DefaultTTL': 0,
                'MaxTTL': 0,
                'ForwardedValues': {
                    'QueryString': True,
                    'Cookies': {
                        'Forward': 'none',
                        'WhitelistedNames': {
                            'Quantity': 0,
                            'Items': [
                                '',
                            ]
                        }
                    }, 
                    'Headers': {
                    'Quantity': 1,
                    'Items': [
                        'Authorization',
                    ]
                },
                },              
            },
            'Comment': application,
            'Enabled': True,
            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': False,
                'ACMCertificateArn': certificate_arn,
                'SSLSupportMethod': 'sni-only',
                'MinimumProtocolVersion': 'TLSv1.2_2019'
            },
            'HttpVersion': 'http2',
            'IsIPV6Enabled': True
        }
    )

    return response   

def lambda_handler(event, context):
    payload = json.loads(event['body'])

    try:
        domain = payload['domain']
        url    = payload['url']
        origin = payload['origin']
        application = payload['application']
        certificate_arn = ''
    except Exception as e:
        print(e)        
    
    certificate_arn = get_certificate_arn(domain)
    if certificate_arn != False:
        cloudfront = create_cloudfront(url, certificate_arn, origin, application)
        endpoint = cloudfront["Distribution"]["DomainName"]
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(endpoint)
        }
    else:
         return {
            "statusCode": 502,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": 'Failed to create Cloudfront distribution, the certificate could not be obtained or has not been issued yet.'
        }
