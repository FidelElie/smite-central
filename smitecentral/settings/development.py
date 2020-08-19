""" Development Settings Environment """
import os

from .base import *
from smitecentral.utilities import get_credentials

DEBUG = True

SECRET_KEY = get_credentials("SECRET_KEY")
YOUTUBE_API_KEY = get_credentials("YOUTUBE_API_KEY")
POSTGRES_PASSWORD = get_credentials("POSTGRES_PASSWORD")

DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql",
    "HOST": "localhost",
    "NAME": "smitecentral",
    "PORT": "5432",
    "USER": "postgres",
    "PASSWORD": POSTGRES_PASSWORD
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles/")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles/")

