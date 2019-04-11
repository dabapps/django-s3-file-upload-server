from django.conf.urls import include, url


urlpatterns = [
    url(r'^s3_file_uploads/', view=include('s3_file_uploads.urls')),
]
