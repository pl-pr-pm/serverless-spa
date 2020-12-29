import boto3
import uuid
import json
import logging
import os
import datetime
import decimal
from botocore.exceptions import ClientError

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
        photo_id = event['pathParameters']['id']
        try:
            response = table.get_item(
                Key = {
                    'photo_id':photo_id
                }
            )
            
            logger.info(response)
            
            if 'Item' not in response:
                logging.info("Specified key is not found.")
                response = {
                    'statusCode':'404',
                    'body':'Not Found',
                    'headers': {
                        'Content-Type' : 'application/json',
                        'Access-Control-Allow-Origin':'*'
                    },
                }
                return response
        
            else:
                response = table.delete_item(
                    Key = {
                        'photo_id':photo_id
                    }
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
              logging.info(
                'Item (photo_id = ' + photo_id + ') is sucessfully deleted'
                )
              response = {
                    'statusCode': '204',
                    'body': '',
                    'headers': {
                        'Content-Type': 'application/json'
                    }
                }
              return response
            
    except Exception as e:
        logging.error("type: %s", type(e))
        logging.error(e)