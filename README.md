Django S3 File Uploads
===================
[![Build Status](https://travis-ci.com/dabapps/django-s3-file-uploads.svg?token=k7ApnEQbpXLoWVm5Bc9o&branch=master)](https://travis-ci.com/dabapps/django-s3-file-uploads)

Upload files to AWS - straight from the browser

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
```

These can be applied with catfish e.g.

```shell
$ ctf project config --set KEY=VALUE
```

The variable `S3_BUCKET_NAME` can be set in `etc/environments/`

## Usage
The flow to be able to upload files from the browser straight to AWS is as follows.
![Flow S3 file uploads](images/flow-s3-file-uploads.png)

This repo will give you access to some useful enpoints.
To make these enpoints available, go to `project/urls.py` and add the following to the `api_url_patterns`
```
  url(r'^s3_file_uploads/', view=include('s3_file_uploads.urls'))
```
This will give you access to
  - `/api/s3_file_uploads/` for getting a url to upload files to AWS to
  - `/api/s3_file_uploads/<file_id>/complete/` for marking an upload as complete
  - `/api/s3_file_uploads/<file_id>/` for getting an AWS endpoint to download files from

**Make sure to run `ctf project run manage.py migrate` to create the `UploadedFile` table in your database.**

We will also abstract out the work that needs to be done on the frontend to make the flow complete. More instructions to follow...
