"""
Create short term uploads locations on S3 (client will do uploading).
Also get short term view urls.
"""
from django.conf import settings
import boto3
from io import BytesIO
from s3_file_uploads.constants import PRIVATE


class S3AssetHandler:
    UPLOAD_ENDPOINT_EXPIRES = 300
    DOWNLOAD_ENDPOINT_EXPIRES = 300

    def __init__(self, id: str) -> None:
        self.id = str(id)  # coerce just in case someone passes in a UUID()
        self.s3 = boto3.client('s3')

    def get_upload_form(self, acl_type=PRIVATE, expiry=UPLOAD_ENDPOINT_EXPIRES) -> dict:
        # NOTE: Used because it's the only way to enforce upload
        #       size on S3.
        return self.s3.generate_presigned_post(
            settings.AWS_BUCKET_NAME,
            self.id,
            Fields={},
            Conditions=[
                {'acl': acl_type},
                ["content-length-range", 1, settings.MAX_FILE_UPLOAD_SIZE],
            ],
            ExpiresIn=expiry
        )

    def get_view_url(self, filename: str, duration=DOWNLOAD_ENDPOINT_EXPIRES) -> str:
        return self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_BUCKET_NAME,
                'Key': self.id,
                'ResponseContentDisposition': "filename=\"{}\"".format(
                    filename
                )
            },
            ExpiresIn=duration
        )

    def get_download_url(self, filename: str, duration=DOWNLOAD_ENDPOINT_EXPIRES) -> str:
        return self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_BUCKET_NAME,
                'Key': self.id,
                'ResponseContentDisposition': "attachment; filename=\"{}\"".format(
                    filename
                )
            },
            ExpiresIn=duration
        )

    def open_content(self) -> BytesIO:
        # NOTE: Downloads file into memory, not suitable for large files!
        data = BytesIO()
        self.s3.download_fileobj(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=self.id,
            Fileobj=data
        )
        return data

    def upload_data(self, content: bytes):
        self.s3.put_object(
            ACL='private',
            Bucket=settings.AWS_BUCKET_NAME,
            Key=self.id,
            Body=content,
            ContentType='application/pdf',
            ContentDisposition='attachment'
        )
