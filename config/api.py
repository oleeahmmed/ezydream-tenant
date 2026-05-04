"""
Django-Bolt entrypoint for ``python manage.py runbolt``.

টেন্যান্ট অথ রুট ``apps.auth.api.attach_auth_routes`` — বাকি সব Django ASGI (``mount_django``)।
"""

from django.core.asgi import get_asgi_application
from django_bolt import BoltAPI
from django_bolt.middleware import DjangoMiddleware

from django_tenants.middleware.main import TenantMainMiddleware

from apps.auth.api import attach_auth_routes
from apps.core.api import attach_core_routes
from apps.businesspartner.api import attach_businesspartner_routes
from apps.finance.api.views import attach_finance_routes
from apps.inventory.api import attach_inventory_routes
from apps.production.api import attach_production_routes
from apps.purchase.api import attach_purchase_routes
from apps.sales.api import attach_sales_routes
from apps.warehouse.api import attach_warehouse_routes

api = BoltAPI(
    middleware=[
        DjangoMiddleware(TenantMainMiddleware),
    ],
)
attach_auth_routes(api)
attach_core_routes(api)
attach_finance_routes(api)
attach_warehouse_routes(api)
attach_inventory_routes(api)
attach_sales_routes(api)
attach_purchase_routes(api)
attach_production_routes(api)
attach_businesspartner_routes(api)
api.mount_django("/", get_asgi_application(), clear_root_path=True)
