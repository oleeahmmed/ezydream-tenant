"""
Django-Bolt entrypoint for ``python manage.py runbolt``.

টেন্যান্ট অথ রুট ``apps.auth.api.attach_auth_routes`` — বাকি সব Django ASGI (``mount_django``)।
"""

from django.core.asgi import get_asgi_application
from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddleware

from django_tenants.middleware.main import TenantMainMiddleware

from apps.auth.api import attach_auth_routes
from apps.foundation.api import attach_foundation_routes

api = BoltAPI(
    middleware=[
        DjangoMiddleware(TenantMainMiddleware),
    ],
)
attach_auth_routes(api)
attach_foundation_routes(api)
api.mount_django("/", get_asgi_application(), clear_root_path=True)
