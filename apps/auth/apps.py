from django.apps import AppConfig


class AuthConfig(AppConfig):
    """
    Tenant-scoped auth (``User`` / ``AbstractTenantEmailUser``). Package ``apps.auth``;
    app label ``tenant_auth`` (``auth`` is reserved for ``django.contrib.auth``).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auth"
    label = "tenant_auth"
    verbose_name = "Auth"
