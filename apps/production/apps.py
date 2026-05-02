from django.apps import AppConfig


class ProductionConfig(AppConfig):
    """SAP Business One–style Production / BOM (tenant schema)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.production"
    label = "tenant_production"
    verbose_name = "Production"
