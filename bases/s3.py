import boto3
from boto3.session import Session
from django.conf import settings


class S3Client(object):
    s3 = boto3.client('s3', aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY'))

    def delete_file(self, key):
        self.s3.delete_object(Bucket=getattr(
            settings, 'AWS_STORAGE_BUCKET_NAME'), Key=key)
