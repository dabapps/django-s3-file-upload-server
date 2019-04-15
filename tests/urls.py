from django.conf.urls import include, url


urlpatterns = [
    url(r'^s3-file-uploads/', view=include('s3_file_uploads.urls')),
]
