Django S3 File Uploads
===================
[![Build Status](https://travis-ci.com/dabapps/django-s3-file-uploads.svg?token=k7ApnEQbpXLoWVm5Bc9o&branch=master)](https://travis-ci.com/dabapps/django-s3-file-uploads)

Upload files to AWS - straight from the browser

THIS IS A WORK IN PROGRESS - CURRENTLY FOR INTERNAL USE AT DABAPPS
(We will also abstract out the work that needs to be done on the frontend to make the flow complete)

## Getting Started

### Installation

Add the following to `requirement.txt`

    git+git://github.com/dabapps/django-s3-file-uploads.git


Add the following to your `settings.py`

    INSTALLED_APPS = (
        ...
        's3_file_uploads',
        ...
    )

    ...

    # S3
    AWS_BUCKET_NAME = env('S3_BUCKET_NAME')
    AWS_STORAGE_BUCKET_NAME = AWS_BUCKET_NAME
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

Make sure to set a `MAX_FILE_UPLOAD_SIZE` in `settings.py` as well.

### Setup environment variables

You will need to create an AWS bucket and set the following env variables

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
S3_BUCKET_NAME
```

## Usage
The flow to be able to upload files from the browser straight to AWS is as follows.
![Flow S3 file uploads](images/flow-s3-file-uploads.png)

This repo will give you access to some useful enpoints.
To make these endpoints available, add the following to the `urlpatterns`
```
  url(r'^s3-file-uploads/', view=include('s3_file_uploads.urls'))
```
This will give you access to
  - `/s3-file-uploads/` for getting a url to upload files to AWS to
  - `/s3-file-uploads/<file_id>/complete/` for marking an upload as complete
  - `/s3-file-uploads/<file_id>/` for getting an AWS endpoint to download files from

**Make sure to run migrations to create the `UploadedFile` table in your database.**


## Code of conduct

For guidelines regarding the code of conduct when contributing to this repository please review [https://www.dabapps.com/open-source/code-of-conduct/](https://www.dabapps.com/open-source/code-of-conduct/)
