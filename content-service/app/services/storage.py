import boto3
from botocore.client import Config
from app.core.config.env import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.AWS_S3_ENDPOINT,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"),
    region_name=settings.AWS_REGION,
)

def generate_presigned_url(filename: str, content_type: str):
    try:
        url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.MINIO_TEMP_BUCKET,
                "Key": filename,
                "ContentType": content_type
            },
            ExpiresIn=900,  # 15 minutes
        )
        return url
    except Exception as e:
        print("Error generating pre-signed URL:", e)
        raise
