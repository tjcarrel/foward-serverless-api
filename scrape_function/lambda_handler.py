import os
import re
import time
import json
import boto3
from selenium import webdriver
from botocore.exceptions import ClientError
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Grab Environment variables
db_table = os.environ['DB_TABLE']
db_primary_key = os.environ['DB_PRIMARY_KEY']
twitter_regex = os.environ['TWITTER_USERNAME_REGEX']

# Create client for calling DynamoDB
client = boto3.client('dynamodb')

# Event handler for when the Lambda gets invoked
def lambda_handler(event, context):
    # Extract handle from request
    handle = extract_parameter(event, 'handle')

    # Check if a valid handle was provided
    if not handle or not re.match(twitter_regex, handle):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Must provide a valid twitter handle'}),
        }
    
    # Create a browser instance for scraping
    driver = get_driver()

    # Call helper to extract profile_url for the user
    profile_url = get_profile_url(driver, handle)

    if not profile_url:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Unable to scrape profile image for user'}),
        }

    # If valid, insert into DB
    db_error = insert_in_db(handle, profile_url)

    if db_error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error :('}),
        }

    return {
        'statusCode': 200,
        'body': json.dumps({
            'handle': handle,
            'profileImageUrl': profile_url
        }),
    }

# Extracts the request body parameter from the Lambda event object
# Returns the desired parameter as string
def extract_parameter(event, parameter):
    try:
        request_payload = json.loads(event['body'])
        desired_parameter = request_payload[parameter]

        return desired_parameter
    except KeyError:
        return ''

# Inserts new item into the database
# Returns an error message if one occured - empty string means no error
def insert_in_db(handle, profile_url) -> str:
    try:
        item = {
            db_primary_key: { 'S': handle },
            'profileImageUrl': { 'S': profile_url }
        }
        
        client.put_item(TableName=db_table, Item=item)

        return ''

    except ClientError as err:
        return err.response['Error']['Message']


# Makes request to user's twitter profile and extracts the url for their profile image
# Returns the profile_url if found
def get_profile_url(driver, handle):
    driver.get(f'https://twitter.com/{handle}')

    # Allow JS to load on page
    time.sleep(5)

    # Search for the element that displays the user's image
    elements = driver.find_elements(By.TAG_NAME, 'img')

    profile_url = ''

    for element in elements:
        image_src = element.get_attribute('src')

        # Once the 200x200 image is found - it's super easy to grab the larger version ;)
        if '200x200' in image_src:
            profile_url = image_src.replace('200x200', '400x400')
            break

    return profile_url


# Creates a new browser instance to perform the scraping
def get_driver():
    service = Service('/opt/chromedriver')

    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'

    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-tools')
    options.add_argument('--no-zygote')
    options.add_argument('--single-process')
    options.add_argument('--remote-debugging-port=9222')

    driver = webdriver.Chrome(service=service, options=options)

    return driver
