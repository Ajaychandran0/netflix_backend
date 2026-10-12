import boto3

from app.core.config import static_config

def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=str(static_config.aws_s3_endpoint),
        aws_access_key_id=static_config.aws_access_key_id,
        aws_secret_access_key=static_config.aws_secret_access_key,
        region_name=static_config.aws_region
)
    