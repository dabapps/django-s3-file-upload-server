from rest_framework import serializers

from s3_file_uploads.models import UploadedFile


class UploadedFilePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def get_queryset(self):
        request = self.context['request']
        return UploadedFile.objects.filter(user=request.user)

