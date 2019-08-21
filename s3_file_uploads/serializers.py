from rest_framework import serializers
from s3_file_uploads.constants import ACCESS_CONTROL_TYPES
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
            'file_path',
            'user',
        ]
        read_only_fields = [
            'id',
            'modfied',
            'created',
            'file_name',
            'file_path',
            'file_key'
        ]

class AccessControlListSerializer(serializers.Serializer):
    acl = serializers.CharField(required=False)

    def validate_acl(self, value):
        if value not in ACCESS_CONTROL_TYPES:
            raise serializers.ValidationError('{acl} is not a valid acl type'.format(acl=value))
        return value
