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

def lambda_handler(event, context):
    logger.debug("Received event: %s", json.dumps(event))

    # Validate incoming query parameter
    if "q" not in event or not event["q"]:
        logger.error("No search query provided in request.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No search query provided."})
        }

    query = event["q"]
    logger.info("Search query: %s", query)

    # Step 1: Disambiguate query using Lex
    labels = get_labels_from_lex(query)
    if not labels:
        logger.info("No labels found from Lex for query: %s", query)
        return {
            "statusCode": 200,
            "body": json.dumps({"results": []})  # Return empty array if no keywords found
        }

    logger.info("Extracted labels from Lex: %s", labels)

    # Step 2: Search for photos in OpenSearch
    search_results = search_photos_in_opensearch(labels)
    logger.info("Search results: %s", search_results)

    return {
        "statusCode": 200,
        "body": json.dumps({"results": search_results})  # Return search results
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


def search_photos_in_opensearch(labels):
    """
    Searches the OpenSearch index for photos using the extracted labels.
    """
    results = []
    for label in labels:
        search_body = {
            "query": {
                "match": {
                    "labels": label
                }
            }
        }
        try:
            response = requests.post(
                f"{OPENSEARCH_ENDPOINT}/photos/_search",
                auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD),
                headers={"Content-Type": "application/json"},
                json=search_body
            )
            if response.status_code == 200:
                search_data = response.json()
                for hit in search_data.get("hits", {}).get("hits", []):
                    # Append S3 object keys to results
                    results.append(f"s3://cc-hw2-photo-bucket/{hit['_source']['objectKey']}")
            else:
                logger.error("OpenSearch query failed: %s", response.text)
        except Exception as e:
            logger.error("Error querying OpenSearch: %s", str(e))
    return results
