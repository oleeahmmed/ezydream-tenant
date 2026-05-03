from django.apps import AppConfig


class BusinessPartnerConfig(AppConfig):
    """SAP Business One–style business partners (OCRG, OCRD, CRD1), per tenant schema."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.businesspartner"
    label = "tenant_businesspartner"
    verbose_name = "Business partner"
