import os

import dj_database_url

from .base import *

DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

ALLOWED_HOSTS += ['.herokuapp.com']

ADMINS = [
    ("Fidel Elie", "Fidel.Elie2@gmail.com"),
]

DATABASES['default'] = dj_database_url.config(
    default=os.getenv('DATABASE_URL'),
    conn_max_age=600,
    ssl_require=True
)

STATIC_URL = "https://{AWS_S3_CUSTOM_DOMAIN}/static/"
STATICFILES_STORAGE = "smitecentral.storage.StaticStorage"

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
DEFAULT_FILE_STORAGE = 'smitecentral.storage.MediaStorage'

