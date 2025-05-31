import boto3
from botocore.exceptions import NoCredentialsError
import os

s3 = boto3.client(
    "s3",
    region_name="sgp1",
    endpoint_url="https://sgp1.digitaloceanspaces.com",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

try:
    s3.upload_file(
        "config/urls.py", os.getenv("AWS_STORAGE_BUCKET_NAME"), "static/file1.txt"
    )
    print("Upload successful")
except FileNotFoundError:
    print("File not found")
except NoCredentialsError:
    print("Credentials not available")
