from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    """SAP Business One–style Purchase A/P documents (tenant schema)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.purchase"
    label = "tenant_purchase"
    verbose_name = "Purchase (A/P)"
