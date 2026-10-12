import json

from botocore.exceptions import ClientError
from app.core.utils.s3_client import get_s3_client


class BucketService:

    def __init__(self):
        self.s3 = get_s3_client()

    def bucket_exists(self, bucket_name: str) -> bool:
        try:
            self.s3.head_bucket(Bucket=bucket_name)
            return True

        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])

            if error_code == 404:
                return False

            raise

    def create_bucket(self, bucket_name: str) -> None:
        try:
            self.s3.create_bucket(
                Bucket=bucket_name
            )

            print(
                f"Bucket '{bucket_name}' created."
            )

        except ClientError as e:
            print(
                f"Failed to create bucket "
                f"'{bucket_name}': {e}"
            )
            raise

    def ensure_bucket_exists(
        self,
        bucket_name: str,
    ) -> None:
        if not self.bucket_exists(bucket_name):
            self.create_bucket(bucket_name)
        else:
            print(
                f"Bucket '{bucket_name}' already exists."
            )
            
    

    def make_bucket_public_read(self, bucket_name: str) -> None:
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{bucket_name}/*"
                    ],
                }
            ],
        }

        self.s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy),
        )

        print(
            f"Bucket '{bucket_name}' configured "
            f"for public read."
        )
