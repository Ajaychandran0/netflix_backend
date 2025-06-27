from botocore.exceptions import ClientError
from app.core.utils.s3_client import get_s3_client
from app.core.config.env import settings


class BucketService:
    def __init__(self):
        self.s3 = get_s3_client()
        self.bucket_name = settings.S3_TEMP_BUCKET

    def bucket_exists(self) -> bool:
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
            return True
        
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                return False
            raise  # re-raise other errors (e.g., permission issues)

    def create_bucket(self):
        try:
            self.s3.create_bucket(Bucket=self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' created.")
        except ClientError as e:
            print(f"❌ Failed to create bucket: {e}")
            raise

    def ensure_bucket_exists(self):
        if not self.bucket_exists():
            self.create_bucket()
        else:
            print(f"✅ Bucket '{self.bucket_name}' already exists.")
