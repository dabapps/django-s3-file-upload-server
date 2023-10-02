from django.urls import re_path
from s3_file_uploads import views


app_name = 's3_file_uploads'


urlpatterns = [
    re_path(r'^$', view=views.UploadedFileCreateView.as_view(), name='upload-file-create'),
    re_path(r'^(?P<file_id>[0-9a-f-]+)/$', view=views.UploadedFileFetchView.as_view(), name='upload-file-fetch'),
    re_path(r'^(?P<file_id>[0-9a-f-]+)/complete/$', view=views.UploadedFileUploadCompleteView.as_view(), name='upload-file-complete'),
]
