import logging
import os
import json

from todos import decimalencoder
import boto3
dynamodb = boto3.resource('dynamodb')


def translate(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id'],
        }
    )

    try:
        item = result['Item']

        # comprehend origin language
        comprehend = boto3.client(service_name='comprehend',
                                  region_name='us-east-1')
        related = comprehend.detect_dominant_language(Text=item['text'])

        # translate result text
        translate = boto3.client(service_name='translate',
                                 region_name='us-east-1',
                                 use_ssl=True)

        translation = translate.translate_text(
            Text=item['text'],
            SourceLanguageCode=related['Languages'][0]['LanguageCode'],
            TargetLanguageCode=event['pathParameters']['lang'])

        item['text'] = translation['TranslatedText']

        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(item,
                               cls=decimalencoder.DecimalEncoder)
        }

        return response

    except Exception as e:
        logging.error(str(e))
        raise Exception("[ErrorMessage]: " + str(e))
