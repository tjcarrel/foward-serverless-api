import os
import json
import boto3
from botocore.exceptions import ClientError

# Grab environment variables
db_table = os.environ['DB_TABLE']
db_primary_key = os.environ['DB_PRIMARY_KEY']

# Create client for calling DynamoDB
client = boto3.client('dynamodb')

# Event handler for when the Lambda gets invoked
def lambda_handler(event, context):
    lastKey = ''

    # Check to see if user provided a lastKey value in request
    query_params = event['queryStringParameters']

    if query_params and 'lastKey' in query_params:
        lastKey = query_params['lastKey']

    # Make request to db 
    users, updatedLastKey, err = get_all_users(lastKey)

    if err:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error :('}),
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'lastKey': updatedLastKey,
            'users': users
        }),
    }

# Makes request to db for all values, using lastKey if one is provided
# Returns three values - users (list), updatedLastKey (str), err (str) 
def get_all_users(lastKey):
    try:
        # Use lastKey in request to db if one was provided
        response = client.scan(TableName=db_table) if not lastKey else client.scan(TableName=db_table, ExclusiveStartKey=lastKey)

        updatedLastKey = ''
        data = response['Items']

        # Check if a new lastKey is provided in response
        if 'LastEvaluatedKey' in response:
            updatedLastKey = response.LastEvaluatedKey

        users = []

        # Iterate through items and grab user data
        for user in data:
            users.append({
                'handle': user['user']['S'],
                'profileImageUrl': user['profileImageUrl']['S'],
            })

        return users, updatedLastKey, ''

    except ClientError as err:
        return [], '', err.response['Error']['Message']
