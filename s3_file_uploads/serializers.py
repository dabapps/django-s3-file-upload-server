from rest_framework import serializers
from s3_file_uploads.models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):

    file_name = serializers.CharField(source='file.name', read_only=True)
    file = serializers.URLField(source='get_download_url', read_only=True)

    class Meta:
        model = UploadedFile
        fields = [
            'id',
            'created',
            'modified',
            'file_key',
            'file',
            'filename',
            'file_name',
            'file_path'
        ]
        read_only_fields = [
            'id',
            'modfied',
            'created',
            'file_name',
            'file_path',
            'file_key'
        ]
