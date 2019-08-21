DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',

    'tests',
    's3_file_uploads',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

TEMPLATES = [
    {"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True}
]

ROOT_URLCONF = 'tests.urls'

SECRET_KEY = "abcde12345"

AWS_BUCKET_NAME = "AWS_BUCKET_NAME"
AWS_STORAGE_BUCKET_NAME = AWS_BUCKET_NAME
AWS_ACCESS_KEY_ID = "AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "AWS_SECRET_ACCESS_KEY"

MAX_FILE_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

ACCESS_CONTROL_TYPES = ['private', 'public-read', 'public-read-write', 'authenticated-read']
