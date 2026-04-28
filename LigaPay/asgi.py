"""
ASGI config for LigaPay project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

import django
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LigaPay.settings.dev')
django.setup()

# Получаем стандартное ASGI-приложение Django
django_asgi_app = get_asgi_application()
from django.apps import apps
from django.conf import settings

print("ASGI FILE LOADED")
print("DJANGO_SETTINGS_MODULE =", os.environ.get("DJANGO_SETTINGS_MODULE"))
print('SETTINGS_MODULE =', os.environ.get('DJANGO_SETTINGS_MODULE'))
print('apps.ready =', apps.ready)
print('contenttypes in INSTALLED_APPS =', 'django.contrib.contenttypes' in settings.INSTALLED_APPS)
print('INSTALLED_APPS size =', len(settings.INSTALLED_APPS))


from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from chat import routing


application = ProtocolTypeRouter(
    {
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
        ),
    }
)
