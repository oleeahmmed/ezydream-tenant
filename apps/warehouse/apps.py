from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    """SAP Business One–style warehouse master (OWHS), per tenant schema."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.warehouse"
    label = "tenant_warehouse"
    verbose_name = "Warehouse"
