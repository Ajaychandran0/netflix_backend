import boto3
from app.core.config.env import settings


def get_s3_client():
    session = boto3.session.Session()
    return session.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT,
        region_name=settings.AWS_REGION,
    )


def get_s3_public_client():
    session = boto3.session.Session()
    return session.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_PUBLIC_ENDPOINT,
        region_name=settings.AWS_REGION,
    )
