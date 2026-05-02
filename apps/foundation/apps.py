from django.apps import AppConfig


class FoundationConfig(AppConfig):
    """ERP master data (tenant schema). Label avoids clashing with generic names."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.foundation"
    label = "tenant_foundation"
    verbose_name = "Foundation"
