from django.apps import AppConfig


class SalesConfig(AppConfig):
    """SAP Business One–style Sales A/R documents (tenant schema)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sales"
    label = "tenant_sales"
    verbose_name = "Sales (A/R)"
