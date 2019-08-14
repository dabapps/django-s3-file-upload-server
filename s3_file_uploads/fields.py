from rest_framework import serializers

class UploadedFilePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def __init__(self, **kwargs):
        request = self.context['request']
        self.queryset = UploadedFile.objects.filter(user=request.user)
        super(PrimaryKeyRelatedField, self).__init__(**kwargs)
