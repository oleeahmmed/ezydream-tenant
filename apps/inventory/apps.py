from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """SAP Business One–style inventory (tenant schema)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.inventory"
    label = "tenant_inventory"
    verbose_name = "Inventory"
