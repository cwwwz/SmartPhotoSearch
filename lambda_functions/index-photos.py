import json
import boto3
import requests
from datetime import datetime

# Initialize AWS clients
rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

# OpenSearch domain
OPENSEARCH_ENDPOINT = ""
OPENSEARCH_USERNAME = ""  
OPENSEARCH_PASSWORD = ""

def lambda_handler(event, context):
    try:
        # Get details from the event
        if "body" in event:
            # Parse request body for PUT API call
            body = json.loads(event["body"])
            bucket = body["bucket"]
            photo = body["key"]
            user_labels = body.get("customLabels", [])
        else:
            # Handle S3 event trigger
            s3_details = event['Records'][0]['s3']
            bucket = s3_details['bucket']['name']
            photo = s3_details['object']['key']
            user_labels = []

        # Step 1: Fetch custom metadata from S3
        metadata_response = s3.head_object(Bucket=bucket, Key=photo)
        custom_labels = metadata_response.get('Metadata', {}).get('customlabels', '').split(',')
        custom_labels = [label.strip() for label in custom_labels if label]

        # Step 2: Use Rekognition to detect labels
        rekognition_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
            MaxLabels=10,
            MinConfidence=80
        )
        rekognition_labels = [label['Name'] for label in rekognition_response['Labels']]

        # Combine Rekognition labels, custom labels, and user input labels
        combined_labels = custom_labels + rekognition_labels + user_labels
        deduplicated_labels = list(set([label.lower() for label in combined_labels]))
        print(f"Final Deduplicated Labels for {photo}: {deduplicated_labels}")

        # Step 3: Prepare metadata for indexing
        photo_metadata = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimestamp": datetime.now().isoformat(),
            "labels": deduplicated_labels
        }

        # Step 4: Index metadata into OpenSearch
        response = requests.post(
            OPENSEARCH_ENDPOINT,
            auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD), 
            headers={"Content-Type": "application/json"},
            json=photo_metadata
        )

        # Log the result
        print(f"OpenSearch Response: {response.status_code}, {response.text}")
        return {"statusCode": response.status_code, "body": response.text}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}