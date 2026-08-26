"""
WSGI config for GymManagementSystem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymManagementSystem.settings')

# application = get_wsgi_application()

import os

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'GymManagementSystem.settings'
)

try:
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()

except Exception as e:
    print("========== DJANGO STARTUP ERROR ==========")
    print(type(e).__name__)
    print(str(e))
    print("==========================================")
    raise