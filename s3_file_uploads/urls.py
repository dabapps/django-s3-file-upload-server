from django.conf.urls import url
from s3_file_uploads import views


app_name = 's3_file_uploads'


urlpatterns = [
    url(r'^$', view=views.UploadedFileCreateView.as_view(), name='upload-file-create'),
    url(r'^(?P<file_id>[0-9a-f-]+)/$', view=views.UploadedFileFetchView.as_view(), name='upload-file-fetch'),
    url(r'^(?P<file_id>[0-9a-f-]+)/complete/$', view=views.UploadedFileUploadCompleteView.as_view(), name='upload-file-complete'),
]
