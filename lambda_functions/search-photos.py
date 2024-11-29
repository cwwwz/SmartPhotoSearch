import json
import logging
import requests
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

username = os.getenv("OPENSEARCH_USERNAME")
password = os.getenv("OPENSEARCH_PASSWORD")
endpoint = os.getenv("OPENSEARCH_ENDPOINT")

print(f"Credentials: {username}, {password}, {endpoint}")

LEX_BOT_ID = "UCAEGQJIAF"  
LEX_BOT_ALIAS_ID = "TSTALIASID"  
LEX_LOCALE_ID = "en_US" 
REGION = "us-east-1"

lex_client = boto3.client("lexv2-runtime", region_name=REGION)
s3_client = boto3.client("s3")

def lambda_handler(event, context):
    query = event.get("q")

    if not query:
        logger.error("No search query provided in request.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No search query provided."})
        }

    labels = get_labels_from_lex(query)
    if not labels:
        logger.info("No labels found from Lex for query: %s", query)
        return {
            "statusCode": 200,
            "body": json.dumps({"results": []}) 
        }

    search_results = search_photos_in_opensearch(labels)
    logger.info("Search results: %s", search_results)

    return {
        "statusCode": 200,
        "body": json.dumps({"results": search_results})
    }

def get_labels_from_lex(query):
    try:
        response = lex_client.recognize_text(
            botId=LEX_BOT_ID,
            botAliasId=LEX_BOT_ALIAS_ID,
            localeId=LEX_LOCALE_ID,
            sessionId="session1", 
            text=query
        )
        logger.debug("Lex response: %s", response)

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
            ExpiresIn=3600  
        )
        return url
    except Exception as e:
        logger.error("Error generating pre-signed URL for %s/%s: %s", bucket_name, object_key, str(e))
        return None

def search_photos_in_opensearch(labels):
    results = []
    
    if not labels:
        return results

    must_clauses = [{"match": {"labels": label}} for label in labels]
    search_body = {
        "query": {
            "bool": {
                "must": must_clauses
            }
        }
    }

    try:
        response = requests.post(
            f"{endpoint}/photos/_search",
            auth=(username, password),
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