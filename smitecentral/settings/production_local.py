""" Production Settings Environment In Local Setting """
import os

import dj_database_url

from .base import *
from smitecentral.utilities import get_credentials

DEBUG = True

SECRET_KEY = get_credentials('SECRET_KEY')
YOUTUBE_API_KEY = get_credentials('YOUTUBE_API_KEY')
AWS_ACCESS_KEY_ID = get_credentials('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_credentials('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = get_credentials('AWS_STORAGE_BUCKET_NAME')

AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = get_credentials('CLOUDFRONT_URL')

ALLOWED_HOSTS += ['localhost', '127.0.0.1']

DATABASES['default'] = dj_database_url.config(
    default=get_credentials('DATABASE_URL'),
    conn_max_age=600,
    ssl_require=True
)

STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
STATICFILES_STORAGE = "smitecentral.storage.StaticStorage"


MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
DEFAULT_FILE_STORAGE = 'smitecentral.storage.MediaStorage'
