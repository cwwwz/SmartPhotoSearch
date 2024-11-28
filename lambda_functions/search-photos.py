import json
import logging
import requests
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Constants
OPENSEARCH_ENDPOINT = ""
OPENSEARCH_USERNAME = ""
OPENSEARCH_PASSWORD = ""

LEX_BOT_ID = "" 
LEX_BOT_ALIAS_ID = ""  
LEX_LOCALE_ID = "en_US"  
REGION = "us-east-1"

# Initialize Lex and other clients
lex_client = boto3.client("lexv2-runtime", region_name=REGION)
s3_client = boto3.client("s3")

import json
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    codepipeline = boto3.client('codepipeline')
    
    try:
        logger.debug("Received event: %s", json.dumps(event))
        
        # Extract the CodePipeline job ID
        job_id = event.get('CodePipeline.job', {}).get('id')
        if not job_id:
            raise ValueError("Missing CodePipeline job ID in the event.")

        # Extract the query parameter directly
        query = event.get("q")

        # Validate the query parameter
        if not query:
            logger.error("No search query provided in request.")
            raise ValueError("No search query provided.")

        logger.info("Search query: %s", query)

        # Step 1: Disambiguate query using Lex
        labels = get_labels_from_lex(query)
        if not labels:
            logger.info("No labels found from Lex for query: %s", query)
            codepipeline.put_job_success_result(jobId=job_id)
            return {
                "statusCode": 200,
                "body": json.dumps({"results": []})  # Return empty array if no keywords found
            }

        logger.info("Extracted labels from Lex: %s", labels)

        # Step 2: Search for photos in OpenSearch
        search_results = search_photos_in_opensearch(labels)
        logger.info("Search results: %s", search_results)

        # Notify CodePipeline of success
        codepipeline.put_job_success_result(jobId=job_id)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"results": search_results})  # Return search results
        }

    except Exception as e:
        logger.error("Error processing CodePipeline job: %s", str(e), exc_info=True)
        if 'CodePipeline.job' in event:
            job_id = event['CodePipeline.job']['id']
            codepipeline.put_job_failure_result(
                jobId=job_id,
                failureDetails={
                    'type': 'JobFailed',
                    'message': str(e)
                }
            )
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


def get_labels_from_lex(query):
    """
    Sends the query to Lex and extracts labels from the response.
    """
    try:
        response = lex_client.recognize_text(
            botId=LEX_BOT_ID,
            botAliasId=LEX_BOT_ALIAS_ID,
            localeId=LEX_LOCALE_ID,
            sessionId="session1",  # Session ID can be arbitrary
            text=query
        )
        logger.debug("Lex response: %s", response)

        # Extract labels (slots) from Lex response
        labels = []
        slots = response.get("sessionState", {}).get("intent", {}).get("slots", {})
        for key, value in slots.items():
            if value and "interpretedValue" in value["value"]:
                labels.append(value["value"]["interpretedValue"])
        
        return labels
    except Exception as e:
        logger.error("Error while getting labels from Lex: %s", str(e))
        return []



def generate_presigned_url(bucket_name, object_key):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=3600  # URL validity period in seconds
        )
        return url
    except Exception as e:
        logger.error("Error generating pre-signed URL for %s/%s: %s", bucket_name, object_key, str(e))
        return None

def search_photos_in_opensearch(labels):
    """
    Searches the OpenSearch index for photos that contain all the provided labels.
    """
    results = []
    
    if not labels:
        return results

    # Create a boolean query to match all labels
    must_clauses = [{"match": {"labels": label}} for label in labels]
    search_body = {
        "query": {
            "bool": {
                "must": must_clauses
            }
        }
    }

    try:
        # Perform the OpenSearch query
        response = requests.post(
            f"{OPENSEARCH_ENDPOINT}/photos/_search",
            auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
            headers={"Content-Type": "application/json"},
            json=search_body
        )
        
        if response.status_code == 200:
            search_data = response.json()
            for hit in search_data.get("hits", {}).get("hits", []):
                object_key = hit['_source']['objectKey']
                bucket_name = "cc-hw2-photo-bucket"
                presigned_url = generate_presigned_url(bucket_name, object_key)
                if presigned_url:
                    results.append({
                        "url": presigned_url,
                        "labels": hit['_source'].get('labels', [])
                    })
        else:
            logger.error("OpenSearch query failed: %s", response.text)
    except Exception as e:
        logger.error("Error querying OpenSearch: %s", str(e))
    
    return results