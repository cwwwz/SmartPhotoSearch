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
    codepipeline = boto3.client('codepipeline')
    try:
        # Log the incoming event for debugging
        print(f"Received event: {json.dumps(event)}")

        # Step 1: Extract bucket and photo details from the S3 event
        s3_details = event['Records'][0]['s3']
        bucket = s3_details['bucket']['name']
        photo = s3_details['object']['key']
        print(f"Processing file: {photo} from bucket: {bucket}")

        # Step 2: Fetch custom metadata from S3
        metadata_response = s3.head_object(Bucket=bucket, Key=photo)
        custom_labels = metadata_response.get('Metadata', {}).get('customlabels', '').split(',')
        custom_labels = [label.strip() for label in custom_labels if label]
        print(f"Custom Labels from metadata: {custom_labels}")

        # Step 3: Use Rekognition to detect labels
        rekognition_response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
            MaxLabels=10,
            MinConfidence=80
        )
        rekognition_labels = [label['Name'] for label in rekognition_response['Labels']]
        print(f"Rekognition Labels: {rekognition_labels}")

        # Combine Rekognition labels and custom labels
        combined_labels = custom_labels + rekognition_labels
        deduplicated_labels = list(set([label.lower() for label in combined_labels]))
        print(f"Final Deduplicated Labels for {photo}: {deduplicated_labels}")

        # Step 4: Prepare metadata for indexing
        photo_metadata = {
            "objectKey": photo,
            "bucket": bucket,
            "createdTimestamp": datetime.now().isoformat(),
            "labels": deduplicated_labels
        }
        print(f"Metadata to index: {photo_metadata}")

        # Step 5: Index metadata into OpenSearch
        response = requests.post(
            OPENSEARCH_ENDPOINT,
            auth=(OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD), 
            headers={"Content-Type": "application/json"},
            json=photo_metadata
        )
        print(f"OpenSearch Response: {response.status_code}, {response.text}")
        
        job_id = event['CodePipeline.job']['id']
        codepipeline.put_job_success_result(jobId=job_id)

        # Return success or error based on the OpenSearch response
        if response.status_code == 200 or response.status_code == 201:
            return {"statusCode": 200, "body": "Photo metadata successfully indexed."}
        else:
            print(f"Failed to index metadata: {response.text}")
            return {"statusCode": response.status_code, "body": response.text}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}