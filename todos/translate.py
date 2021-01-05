import logging
import os
import json

from todos import decimalencoder
import boto3
dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def translate(event, context):
    logger.info(event)
    
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id'],
        }
    )
    
    try:
        item = result['Item']
        logger.info(json.dumps(item))
        
        # comprehend origin language
        comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')
        related = comprehend.detect_dominant_language(Text = item['text'])
        logger.info(json.dumps(related))
        
        # translate result text
        translate = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
        translation = translate.translate_text(Text=item['text'], SourceLanguageCode=related['Languages'][0]['LanguageCode'], TargetLanguageCode=event['pathParameters']['lang'])
        logger.info(json.dumps(translation))
        
        item['text'] = translation['TranslatedText']
        
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item,
                               cls=decimalencoder.DecimalEncoder)
        }
        
        return response
        
    except Exception as e:
        raise Exception("[ErrorMessage]: " + str(e))
    