import boto3
import uuid
import json
import logging
import os
import datetime
import decimal
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

"""Loggerをセット"""
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            if obj % 1 > 0:
                return float(obj)
            else:
                return int(obj)

        return super(DecimalEncoder, self).default(obj)

"""
Dynamoインスタンスを作成
Lambda関数のコンテナが再利用された際に置ける処理効率向上の為に、
接続処理をLambda関数のエントリポイントとなるLambda_handler関数内に記述するのではなく、
グローバルスコープで記述とする
"""
dynamodb = boto3.resource('dynamodb', region_name = 'ap-northeast-1')
table = dynamodb.Table(os.getenv('TABLE_NAME'))
    
def lambda_handler(event, context):
    try:
        try:
            response = table.scan(
                FilterExpression=Attr('status').eq('Uploaded')
                )
        except ClientError as e:
            logging.info(e.response['Error']['Message'])
            response = {
                'statusCode':'400',
                'body':e.response['Error']['Message'],
                'headers':{
                        'Content-Type':'application/json',
                        'Access-Control-Allow-Origin':'*'
                    },
                }
            return response
                
        else:
            items = json.dumps(response['Items'], cls=DecimalEncoder)
                
            response = {
                'statusCode':'200',
                'body':items,
                'headers':{
                    'Content-Type':'application/json',
                    'Access-Control-Allow-Origin':'*'
                    },
                }
                
            return response
            
    except Exception as e:
        logging.error("type: %s", type(e))
        logging.error(e)