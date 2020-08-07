import os

from .base import *
from smitecentral.utilities import get_credentials

DEBUG = True

SECRET_KEY = get_credentials("SECRET_KEY")
YOUTUBE_API_KEY = get_credentials("YOUTUBE_API_KEY")

DATABASES = {}

DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": os.path.join(BASE_DIR, "db.sqlite3")
}

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles/")

