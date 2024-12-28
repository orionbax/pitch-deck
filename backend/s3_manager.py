import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('S3Manager')

load_dotenv()

class S3UploadError(Exception):
    """Custom exception for S3 upload errors"""
    pass

class S3Manager:
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        
        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            logger.error("Missing AWS credentials or bucket name")
            raise ValueError("AWS credentials or bucket name not found in environment variables")
        
        logger.info(f"Initializing S3Manager with bucket: {self.bucket_name}")
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )

    def upload_document(self, project_id, file_name, content):
        """Upload a document to S3 and return its key"""
        logger.info(f"Attempting to upload document: {file_name} for project: {project_id}")
        try:
            key = f"{project_id}/documents/{file_name}"
            
            # Convert string content to bytes if necessary
            if isinstance(content, str):
                content = content.encode('utf-8')
                
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content
            )
            logger.info(f"Successfully uploaded document to S3: {key}")
            return key
        except ClientError as e:
            logger.error(f"Failed to upload document to S3: {str(e)}")
            raise

    def get_document(self, key):
        """Retrieve a document from S3"""
        logger.info(f"Attempting to retrieve document with key: {key}")
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            content = response['Body'].read().decode('utf-8')
            logger.info(f"Successfully retrieved document from S3: {key}")
            return content
        except ClientError as e:
            logger.error(f"Failed to retrieve document from S3: {str(e)}")
            raise

    def delete_project_documents(self, project_id):
        """Delete all documents for a project"""
        logger.info(f"Attempting to delete all documents for project: {project_id}")
        try:
            # List all objects with the project prefix
            prefix = f"{project_id}/documents/"
            objects_to_delete = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in objects_to_delete:
                delete_keys = {'Objects': [{'Key': obj['Key']} for obj in objects_to_delete['Contents']]}
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete=delete_keys
                )
                logger.info(f"Successfully deleted documents for project: {project_id}")
            else:
                logger.info(f"No documents found to delete for project: {project_id}")
        except ClientError as e:
            logger.error(f"Failed to delete documents from S3: {str(e)}")
            raise 