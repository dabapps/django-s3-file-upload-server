from django.conf.urls import include
from django.urls import re_path


urlpatterns = [
    re_path(r'^s3-file-uploads/', view=include('s3_file_uploads.urls')),
]
