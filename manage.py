#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kittygram.settings')
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        has_explicit_address = any(
            arg for arg in sys.argv[2:]
            if not arg.startswith('-')
        )
        if not has_explicit_address:
            sys.argv.append('127.0.0.1:80')
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
