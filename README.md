# Python-Serverless-API

The goal of the project was to develop a serverless web service in Python for managing profile pictures from Twitter. 

<br>

## Project Structure

- `template.yaml`
    - AWS SAM template for deploying service
- `scrape_function`
    - `lambda_handler.py` - Lambda handler and function code
    - `Dockerfile` - This function uses the Selenium package which requires additional software that is bundled as an image
- `get_handle_function`
- `get_all_function`
    - `lambda_handler.py` - Lambda handler and function code
    - `requirements.py` - Required Python packages

<br>
<br>

## Run and Test Locally

The web service can be run and tested via the SAM CLI, which requires these tools:

* [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [Python 3](https://www.python.org/downloads/)
* [Docker](https://hub.docker.com/search/?type=edition&offering=community)

Run the following command to build and start a local web server to test the endpoints:

```bash
sam build && sam local start-api
```

While running, make a request to localhost:

```bash
curl -H "Content-Type: application/json" -X POST http://localhost:3000/scrape -d '{"handle": "<handle>"}'
```


<br>
<br>

## Deploy to AWS

Using `template.yaml`, the service can be deployed to an AWS account from the command line.

Build the template then deploy the resources with these two commands:

```bash
sam build -u -t template.yaml 

sam deploy --guided --capabilities CAPABILITY_NAMED_IAM
```


To delete the stack, run the below command:

```bash
sam delete --stack-name <stack-name>
```

<br>
<br>

## API Specification

<br>

### Scrape profile image for handle

#### Request
`POST /scrape/`

     curl -H "Content-Type: application/json" -X POST http://localhost:3000/scrape -d '{"handle": "<handle>"}'

#### Response

    Status: 200 OK
    Content-Type: application/json

    {
        "handle": "<handle>", 
        "profileUrl": "..."
    }

<br>

### Get profile image url for handle

#### Request

`GET /user/{handle}/profile_pic`

    curl -i -H 'Accept: application/json' http://localhost:3000/user/<handle>/profile_pic

#### Response

    Status: 200 OK
    Content-Type: application/json

    {
        "profile_url": "..."
    }

<br>

### Get all stored users

#### Request

`GET /users`

    curl -i -H 'Accept: application/json' http://localhost:3000/users?lastKey={optionalKey}

#### Response

    Status: 200 OK
    Content-Type: application/json

    [
        {
            "lastKey": "<lastKey or ''>"
            "users": {
                "handle": "...".
                "profile_url": "..."
            }
        }
    ]

<br>
<br>

## Design Choices

- AWS SAM
    - Allows for efficient packaging of cloud resources with the ability to test your application locally. I did checkout Serverless but ultimately prefer CloudFormation + SAM.
- Lambda Structure
    - There were many ways to service through Lambda. Due to the size of the project, I decided to make each API route its own function. This allows each function to have dedicated logging and error handling, and minor changes to one from causing bugs in another. As applications grow and the code overlap becomes larger, it could be advantageous to bundle them together.
-  DynamoDB
    - To fullfill the serverless requirements and have the ability to deploy the entire service from one file, DynamoDB was a good choice that fit the use case. However, for larger-scale applications I'd prefer to use MongoDB for a NoSQL DB or explore SQL options.
