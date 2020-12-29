import boto3
import uuid
import json
import logging
import os
import datetime
from botocore.exceptions import ClientError

"""Loggerをセット"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)

"""
Dynamoインスタンスを作成
Lambda関数のコンテナが再利用された際に置ける処理効率向上の為に、
接続処理をLambda関数のエントリポイントとなるLambda_handler関数内に記述するのではなく、
グローバルスコープで記述とする
"""
dynamodb = boto3.resource('dynamodb', region_name = 'ap-northeast-1')
table = dynamodb.Table(os.getenv('TABLE_NAME'))

def generate_id():
    return str(uuid.uuid4())

def get_timestamp():
    """
    DyanamoDB tableのレコード用にタイムスタンプを生成
    DyanamoDBでは、float型をサポートしていない為、int型へ変換処理を加える
    """
    now = datetime.datetime.utcnow()
    return int(now.timestamp())

def get_presigned_url(bucket_name, key, type):
    s3 = boto3.client('s3', region_name = 'ap-northeast-1')
    url = s3.generate_presigned_url(
        ClientMethod = 'put_object',
        Params = {'Bucket' : bucket_name, 'Key' : key, 'ContentType' : type},
        ExpiresIn = 3600,
        HttpMethod = 'PUT'
    )
    return url
    
def lambda_handler(event, context):
    logger.info(event)
    body = json.loads(event['body'])
    ext = body['type'].split('/')[1]
    photp_id = generate_id()
    url = get_presigned_url(os.getenv('BUCKET_NAME'), photp_id + "." + ext, body['type'])
    item = {
        'photo_id':photp_id,
        'timestamp':get_timestamp(),
        'status':'Waiting',
        'type':body['type'],
        'size':body['size']
    }
    try:
        table.put_item(
            Item = item
            )
    except ClientError as e:
        logger.info(e.response['Error']['Message'])
        response = {
            'statusCode': '400',
            'body': e.response['Error']['Message'],
            'headers': {
                'Content-Type':'application/json' ,
                'Access-Control-Allow-Origin' : '*'
            }
        }
        return response
    else:
        item['signed_url'] = url
        response = {
            'statusCode': '200',
            'body': json.dumps(item),
            'headers': {
                'Content-Type':'application/json' ,
                'Access-Control-Allow-Origin' : '*'
            },
        }
    return response
