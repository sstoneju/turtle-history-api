import sys
from sys import platform
import os
from datetime import datetime
import time
import json
import asyncio
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from loguru import logger

ENV = os.getenv('ENV','')
ACCESS_KEY = os.getenv('ACCESS_KEY','')
SECRET_KEY = os.getenv('SECRET_KEY','')
# default region of 'seoul'
REGION = os.getenv('REGION','ap-northeast-2')

class BaseStorageService:
    """ 나중에 sheet 별로 Service를 만들 수 있지 않을까 헤서 Base로 만들었다.
    """
    def __init__(self, name):
        """ TODO singleton으로 작성하기.
        """
        self.name = name or ''
        # self.session = boto3.session.Session()
        if ENV == 'local':
            """
            Auto detecting AWS keys with default
            """
            self.dynamo = boto3.resource('dynamodb')
            self.client = boto3.client('dynamodb')
        else:
            self.dynamo = boto3.resource('dynamodb', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
            self.client = boto3.client('dynamodb', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        self.table = self.dynamo.Table(name)


class StorageService(BaseStorageService):
    """
    참고
    https://docs.aws.amazon.com/ko_kr/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html

    # 멀티 쓰레딩에서 사용 가능하게 적용하기
    import boto3
    import boto3.session
    import threading

    class MyTask(threading.Thread):
        def run(self):
            session = boto3.session.Session()
            s3 = session.resource('s3')
            # ... do some work with S3 ...

    ## Note
    # Resources are not thread safe. These special classes contain additional meta data 
    that cannot be shared between threads. When using a Resource, 
    it is recommended to instantiate a new Resource for each thread, 
    as is shown in the example above.
    # Low-level clients are thread safe. When using a low-level client, it is recommended 
    to instantiate your client then pass that client object to each of your threads.
    """
    def __init__(self, name):
        super().__init__(name) # Overload of parents


    def put_item(self, item):
        try:
            response = self.table.put_item(Item=item)
            meta = response['ResponseMetadata'] if 'ResponseMetadata' in response else {}
            status = meta['HTTPStatusCode'] if 'HTTPStatusCode' in meta else 500
        except ClientError as error:
            returns_client_error(error, { "item": {}, "status_code": 500 })
        except BaseException as error:
            returns_unknown_error(error, { "item": {}, "status_code": 500 })
        return { "item": item, "status_code": status }
        

    def put_bulk(self, items):
        try:
            temps = []
            if not isinstance(items, list):
                raise TypeError
            if int(len(items)/25) > 1:
                for div in range(0, int(len(items)/25)):
                    temps.append(items[div*25:(div+1)*25])
                if int(len(items)%25) >= 1:
                    last_div = int(len(items)/25) + 1
                    temps.append(items[last_div*25:])
            else:
                temps.append(items)

            logger.info(f'items size: {len(items)}')
            for idx, temp in enumerate(temps):
                logger.info(f'put times: {idx+1}/{(len(items)/25)+1}')
                # TODO improve to async or cellery
                bulk_data = [{'PutRequest': { 'Item': self.get_types(item) }} for item in temp]
                if bulk_data:
                    self.client.batch_write_item( RequestItems={ self.name: bulk_data} )
                time.sleep(1)
        except ClientError as error:
            returns_client_error(error, False)
        except BaseException as error:
            returns_unknown_error(error, False)
        return True
    

    def get_types(self, item):
        result = {}
        for key, val in item.items():
            if isinstance(val, str):
                result[key] = { 'S': f'{val}' }
            elif isinstance(val, list):
                result[key] = { 'L': val }
        return result


    def get_item(self, _id=None, **kwargs):
        try:
            unique_key = {'id': _id }
            if kwargs:
                unique_key.update(kwargs)
            response = self.table.get_item(Key=unique_key)
            item = response['Item'] if 'Item' in response else {}
            meta = response['ResponseMetadata'] if 'ResponseMetadata' in response else {}
            status = meta['HTTPStatusCode'] if 'HTTPStatusCode' in meta else 500
        except ClientError as error:
            returns_client_error(error, { "item": {}, "status_code": 500 })
        except BaseException as error:
            returns_unknown_error(error, { "item": {}, "status_code": 500 })
        return { 'item': item, 'status_code': status }


    def get_bulk(self, **kwargs):
        """ 참고: 다른 컬럼을 이용해 찾기위해선 global index애 작성해줘야한다.
        https://stackoverflow.com/questions/34171563/how-do-i-query-aws-dynamodb-in-python
        partition_key와 sort_key로 검색을 해야한다.
        """
        try:
            # TODO 이 부분을 좀 더 레거시하게 작성해야겠다.
            # ConditionExpression에 대해서 파싱이 가능한것인지 확인을 좀 해봐야겠다.
            response = self.table.query(
                KeyConditionExpression=Key('id').eq('0') & Key('bookmark').eq('0')
                )
            data = response['Items']

            # LastEvaluatedKey indicates that there are more results
            while 'LastEvaluatedKey' in response:
                response = self.table.query(ExclusiveStartKey=response['LastEvaluatedKey'])
                data.update(response['Items'])
            meta = response['ResponseMetadata'] if 'ResponseMetadata' in response else {}
            status = meta['HTTPStatusCode'] if 'HTTPStatusCode' in meta else 500
        except ClientError as error:
            returns_client_error(error, { "item": [], "status_code": 500 })
        return { 'item': data, "status_code": status }
    

    def update_item(self, _id, item):
        response = self.table.update_item(
            Key={
                'id': _id,
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    
    def update_bulk(self):
        return self



"""####################################
            Utils for dynamoDB
"""####################################
def returns_client_error(error, returns=None):
    ERROR_HELP_STRINGS = {
        # Operation specific errors
        'ConditionalCheckFailedException': 'Condition check specified in the operation failed, review and update the condition check before retrying',
        'TransactionConflictException': 'Operation was rejected because there is an ongoing transaction for the item, generally safe to retry with exponential back-off',
        'ItemCollectionSizeLimitExceededException': 'An item collection is too large, you\'re using Local Secondary Index and exceeded size limit of items per partition key.' +
                                                    ' Consider using Global Secondary Index instead',
        # Common Errors
        'InternalServerError': 'Internal Server Error, generally safe to retry with exponential back-off',
        'ProvisionedThroughputExceededException': 'Request rate is too high. If you\'re using a custom retry strategy make sure to retry with exponential back-off.' +
                                                'Otherwise consider reducing frequency of requests or increasing provisioned capacity for your table or secondary index',
        'ResourceNotFoundException': 'One of the tables was not found, verify table exists before retrying',
        'ServiceUnavailable': 'Had trouble reaching DynamoDB. generally safe to retry with exponential back-off',
        'ThrottlingException': 'Request denied due to throttling, generally safe to retry with exponential back-off',
        'UnrecognizedClientException': 'The request signature is incorrect most likely due to an invalid AWS access key ID or secret key, fix before retrying',
        'ValidationException': 'The input fails to satisfy the constraints specified by DynamoDB, fix input before retrying',
        'RequestLimitExceeded': 'Throughput exceeds the current throughput limit for your account, increase account level throughput before retrying',
    }
    error_code = error.response['Error']['Code']
    error_message = error.response['Error']['Message']
    
    error_help_string = ERROR_HELP_STRINGS[error_code]

    logger.error(f'[{error_code}] {error_help_string}. Error message: {error_message}')
    return returns

def returns_unknown_error(error, returns=None):
    logger.error(f"Unknown error while putting item: {error}")
    return returns

def column_mapper_to(sheet:str, item:dict, partition_key:str):
    subs = {}
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        path = './map_sheet/'
    elif platform == "win32":
        path = '.\\map_sheet\\'
    filepath = f'{path}{sheet}'
    with open(filepath, 'r+', encoding='utf-8') as fp:
        sheet_data = json.loads(fp.read())
        for key, val in sheet_data.items():
            if key in item:
                # filterd empty column.
                subs[val] = item[key]
    if 'id' not in subs:
        partition_key = partition_key if partition_key else ''
        if not subs['ticker']:
            subs['ticker'] = partition_key
        subs['id'] = subs['ticker']
    return subs


def migrate_for(sheet:str, item: dict):
    sheet = 'pools.json'
    if platform == "linux" or platform == "linux2" or platform == "darwin":
        path = './map_sheet/'
    elif platform == "win32":
        path = '.\\map_sheet\\'
    filepath = f'{path}{sheet}'
    with open(filepath, 'r+', encoding='utf-8') as fp:
        sheet_data = json.loads(fp.read())
        for key, val in sheet_data.items():
            item[key] = val
    return item

def convert_string_to_date(str_date:str, form='%Y%m%d'):
    str_date = ''.join(str_date.split('.')) if str_date.split('.') else str_date
    str_date = ''.join(str_date.split('-')) if str_date.split('-') else str_date
    str_date = ''.join(str_date.split('/')) if str_date.split('/') else str_date
    date_obj = datetime.strptime(str_date, form)
    return date_obj