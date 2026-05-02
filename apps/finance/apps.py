from django.apps import AppConfig


class FinanceConfig(AppConfig):
    """SAP Business One–style finance (tenant schema)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.finance"
    label = "tenant_finance"
    verbose_name = "Finance"
