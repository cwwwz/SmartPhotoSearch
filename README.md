# Smart Photo Search App

**PhotoSearchApp** is a serverless application designed to enable users to upload photos, perform keyword-based searches, and retrieve relevant images based on labels detected through AI-powered processing. This project integrates various AWS services to provide a scalable, efficient, and automated solution for photo storage, indexing, and search.

---

## Demo Screenshots
<img width="1504" alt="Screenshot 2024-11-29 at 12 50 29 AM" src="https://github.com/user-attachments/assets/94033051-2d09-4e10-9088-1101b792aa78">

<img width="1495" alt="Screenshot 2024-11-29 at 12 50 08 AM" src="https://github.com/user-attachments/assets/34f47893-9e5e-47a3-8d8e-479a5010c539">

---

## Features

- **Photo Upload**: Users can upload photos to an S3 bucket.
- **AI Label Detection**: AWS Rekognition analyzes uploaded photos to detect labels.
- **Custom Metadata**: Users can optionally provide custom labels when uploading photos.
- **Photo Search**: Users can search for photos by keywords. The search combines user-provided labels and Rekognition-detected labels to match results.
- **Search Results**: Photos matching the search criteria are retrieved from the S3 bucket and displayed.

---

## AWS Services Used

1. **Amazon S3**  
   - Stores uploaded photos and manages object metadata for custom labels.
   - Triggers the **Index Photos** Lambda function upon new uploads.

2. **AWS Rekognition**  
   - Detects labels for photos uploaded to S3 using image recognition.

3. **AWS Lambda**  
   - **Index Photos**: Processes new photo uploads, combines Rekognition-detected and custom labels, and indexes photo metadata into OpenSearch.
   - **Search Photos**: Handles user search queries, integrates with Lex for keyword disambiguation, and retrieves matching photo metadata from OpenSearch.

4. **Amazon Lex**  
   - Disambiguates user search queries using natural language processing to extract keywords.

5. **Amazon OpenSearch**  
   - Indexes and stores metadata for uploaded photos, including labels and timestamps.
   - Performs full-text search to find relevant photos based on keywords.

6. **Amazon API Gateway**  
   - Exposes a REST API for photo upload and search functionality.
   - Integrates with Lambda functions for serverless API execution.

7. **CloudWatch Logs**  
   - Monitors and logs the execution of Lambda functions and API Gateway requests for debugging and performance analysis.

---

## How It Works

1. **Photo Upload**
   - A user uploads a photo to the S3 bucket via the `/upload` API endpoint.
   - S3 triggers the **Index Photos** Lambda function to process the photo.

2. **Photo Indexing**
   - **Index Photos** Lambda retrieves Rekognition-detected labels and custom labels from S3 metadata.
   - The Lambda function combines, deduplicates, and indexes the photo metadata into OpenSearch.

3. **Photo Search**
   - A user submits a search query via the `/search` API endpoint.
   - The query is sent to the **Search Photos** Lambda function.
   - The Lambda function uses Lex to disambiguate the query and extract keywords.
   - The keywords are used to search OpenSearch for matching photo metadata.
   - Matching photo results are returned to the user.

---

![1341732510947_ pic](https://github.com/user-attachments/assets/7c763455-6b8c-4abb-8e86-d216456a766a)


