import os
from urllib.parse import urljoin

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage, S3StaticStorage


class StaticStorage(S3StaticStorage):
    location = "backend-static"
    default_acl = "public-read"


class PublicMediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "public-read"
    file_overwrite = False


class CKEditorStorage(S3Boto3Storage):
    """Custom storage for django_ckeditor_5 images."""

    location = os.path.join(settings.MEDIA_ROOT, "ckeditor_5")
    base_url = urljoin(settings.MEDIA_URL, "ckeditor_5/")
