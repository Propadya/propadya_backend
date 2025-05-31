import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = "https://sgp1.digitaloceanspaces.com"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_S3_REGION_NAME = "sgp1"  # Your DigitalOcean region
AWS_S3_SIGNATURE_VERSION = "s3v4"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "region_name": AWS_S3_REGION_NAME,
            "signature_version": AWS_S3_SIGNATURE_VERSION,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "mediafiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "bucket_name": AWS_STORAGE_BUCKET_NAME,
            "endpoint_url": AWS_S3_ENDPOINT_URL,
            "region_name": AWS_S3_REGION_NAME,
            "signature_version": AWS_S3_SIGNATURE_VERSION,
            "custom_domain": f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com",
            # Corrected domain
        },
    },
}
