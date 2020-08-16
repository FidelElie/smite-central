#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from smitecentral.utilities import get_credentials

def main():
    settings_module = os.getenv("DJANGO_SETTINGS_MODULE") or get_credentials("DJANGO_SETTINGS_MODULE")

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
