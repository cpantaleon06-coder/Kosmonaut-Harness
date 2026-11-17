import os

import boto3
from dotenv import load_dotenv

load_dotenv()

s3 = boto3.client(
    "s3",
    region_name=os.environ["AWS_REGION"],
    endpoint_url=os.environ["AWS_ENDPOINT_URL_S3"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
)
BUCKET = os.environ["BUCKET_NAME"]


def upload_archive(key: str, data: bytes) -> None:
    s3.put_object(Bucket=BUCKET, Key=key, Body=data)


def download_archive(key: str) -> bytes:
    return s3.get_object(Bucket=BUCKET, Key=key)["Body"].read()
