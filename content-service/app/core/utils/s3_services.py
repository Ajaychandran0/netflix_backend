from botocore.exceptions import ClientError
from typing import List, Dict
import logging
from app.core.utils.s3_client import get_s3_public_client, get_s3_client
from app.core.config.env import settings
from uuid import uuid4

logger = logging.getLogger("app")

class S3UploadService:
    def __init__(self):
        self.s3 = get_s3_public_client()
        self.s3_internal = get_s3_client()
        self.bucket_name = settings.S3_TEMP_BUCKET

    def initiate_multipart_upload(self, object_name: str) -> str:
        try:
            response = self.s3_internal.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_name
            )
            return response["UploadId"]
        except ClientError as e:
            logger.error(f"Failed to initiate multipart upload: {e}")
            raise

    def generate_presigned_urls(self, object_name: str, upload_id: str, total_parts: int) -> List[Dict]:
        urls = []
        for part_number in range(1, total_parts + 1):
            try:
                url = self.s3.generate_presigned_url(
                    "upload_part",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": object_name,
                        "UploadId": upload_id,
                        "PartNumber": part_number
                    },
                    ExpiresIn=3600
                )
                urls.append({
                    "part_number": part_number,
                    "presigned_url": url
                })
            except ClientError as e:
                logger.error(f"Error generating presigned URL for part {part_number}: {e}")
                raise
        return urls

    def complete_multipart_upload(self, object_name: str, upload_id: str, parts: List[Dict]):
        try:
            response = self.s3_internal.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_name,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts}
            )
            return response
        except ClientError as e:
            logger.error(f"Failed to complete multipart upload: {e}")
            raise

    def abort_multipart_upload(self, object_name: str, upload_id: str):
        try:
            self.s3_internal.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_name,
                UploadId=upload_id
            )
            logger.info(f"Aborted multipart upload for {object_name} with upload_id {upload_id}")
        except ClientError as e:
            logger.error(f"Failed to abort multipart upload: {e}")
            raise
        
    def generate_presigned_url(self, filename: str):
        key = f"uploads/{uuid4()}_{filename}"
        bucket = settings.S3_TEMP_BUCKET
        if not bucket:
            raise ValueError("S3_TEMP_BUCKET is not set in the environment variables.")

        url = self.s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )

        return {"presigned_url": url, "upload_path": key}

