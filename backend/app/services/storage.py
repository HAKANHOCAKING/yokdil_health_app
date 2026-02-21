"""
Storage service for MinIO/S3
"""
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile
import uuid

from app.core.config import settings


class StorageService:
    """Service for file storage operations"""
    
    def __init__(self):
        """Initialize MinIO/S3 client"""
        self.client = boto3.client(
            's3',
            endpoint_url=f"http://{settings.MINIO_ENDPOINT}" if not settings.MINIO_SECURE else f"https://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket_name)
    
    async def upload_pdf(self, file: UploadFile) -> str:
        """Upload PDF to storage and return path"""
        # Generate unique filename
        file_id = str(uuid.uuid4())
        storage_path = f"pdfs/{file_id}/{file.filename}"
        
        # Read file content
        content = await file.read()
        
        # Upload to MinIO
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=storage_path,
            Body=content,
            ContentType='application/pdf',
        )
        
        return storage_path
    
    async def download_pdf(self, storage_path: str) -> bytes:
        """Download PDF from storage"""
        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=storage_path,
            )
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"Failed to download PDF: {str(e)}")
    
    def get_presigned_url(self, storage_path: str, expiration: int = 3600) -> str:
        """Generate presigned URL for temporary access"""
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': storage_path},
            ExpiresIn=expiration,
        )
