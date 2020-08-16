import os

import dj_database_url

from .base import *
from smitecentral.utilities import get_credentials

DEBUG = False

SECRET_KEY = get_credentials('SECRET_KEY')
YOUTUBE_API_KEY = get_credentials('YOUTUBE_API_KEY')
AWS_ACCESS_KEY_ID = get_credentials('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_credentials('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = get_credentials('AWS_STORAGE_BUCKET_NAME')

AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

ALLOWED_HOSTS += ['localhost', '127.0.0.1']

DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "db.sqlite3")
}

STATIC_URL = "https://{AWS_S3_CUSTOM_DOMAIN}/static/"
STATICFILES_STORAGE = "smitecentral.storage.StaticStorage"


MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
DEFAULT_FILE_STORAGE = 'smitecentral.storage.MediaStorage'