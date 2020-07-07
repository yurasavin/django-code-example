#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reestr_proj.settings")

    from django.conf import settings
    from django.core.management import execute_from_command_line
    if settings.DEBUG:
        if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
            import ptvsd

            ptvsd.enable_attach(address=("0.0.0.0", 3000))

    execute_from_command_line(sys.argv)
