import os
import re
import json
import boto3
from botocore.exceptions import ClientError


# Grab environment variables
db_table = os.environ['DB_TABLE']
db_primary_key = os.environ['DB_PRIMARY_KEY']
path_parameter = os.environ['PATH_PARAMETER']
twitter_regex = os.environ['TWITTER_USERNAME_REGEX']

# Create client for calling DynamoDB
client = boto3.client('dynamodb')

# Event handler for when the Lambda gets invoked
def lambda_handler(event, context):
    # Extract handle from event object and validate
    handle = event['pathParameters'][path_parameter]

    if not handle or not re.match(twitter_regex, handle):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Must provide a valid twitter handle'}),
        }
    
    # Grab the user's data from db
    profile_url, error = get_profile_url(handle)

    if error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error :('}),
        }

    if not profile_url:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'error': f'No user for handle {handle} found'
            }),
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'profileImageUrl': profile_url}),
    }

# Retrieves profileImageUrl for user with the provided handle
# Returns url as string if db item is found
def get_profile_url(handle):
    try:
        response = client.get_item(
            TableName=db_table,
            Key={
                db_primary_key: {
                    'S': handle
                }
            }
        )

        item = response.get('Item')

        if not item:
            return '', ''

        return item['profileImageUrl']['S'], ''

    except ClientError as err:
        return '', err.response['Error']['Message']
