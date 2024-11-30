import json
import boto3
import requests
import os
from datetime import datetime

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

username = os.getenv("OPENSEARCH_USERNAME")
password = os.getenv("OPENSEARCH_PASSWORD")
endpoint = os.getenv("OPENSEARCH_ENDPOINT")

def lambda_handler(event, context):
    try:
        print(f"Received event: {json.dumps(event)}")

        s3_details = event['Records'][0]['s3']
        bucket = s3_details['bucket']['name']
        photo = s3_details['object']['key']
        print(f"Processing file: {photo} from bucket: {bucket}")

        metadata_response = s3.head_object(Bucket=bucket, Key=photo)
        custom_labels = metadata_response.get('Metadata', {}).get('customlabels', '').split(',')
        custom_labels = [label.strip() for label in custom_labels if label]
        print(f"Custom Labels from metadata: {custom_labels}")

        rekognition_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
            MaxLabels=10,
            MinConfidence=80
        )
        rekognition_labels = [label['Name'] for label in rekognition_response['Labels']]
        print(f"Rekognition Labels: {rekognition_labels}")

        combined_labels = custom_labels + rekognition_labels
        deduplicated_labels = list(set([label.lower() for label in combined_labels]))
        print(f"Final Deduplicated Labels for {photo}: {deduplicated_labels}")

        photo_metadata = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimestamp": datetime.now().isoformat(),
            "labels": deduplicated_labels
        }
        print(f"Metadata to index: {photo_metadata}")

        response = requests.post(
            f"{endpoint}/photos/_doc/",
            auth=(username, password), 
            headers={"Content-Type": "application/json"},
            json=photo_metadata
        )
        print(f"OpenSearch Response: {response.status_code}, {response.text}")
        
        if response.status_code in (200, 201):
            return {"statusCode": 200, "body": "Photo metadata successfully indexed."}
        else:
            raise Exception(f"Failed to index metadata: {response.text}")

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}