from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.contrib.admin.exceptions import NotRegistered
from django_tenants.admin import TenantAdminMixin
from unfold.admin import ModelAdmin, TabularInline

from .models import Client, Domain

User = get_user_model()


class DomainInline(TabularInline):
    model = Domain
    extra = 0
    fk_name = "tenant"
    tab = True


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, ModelAdmin):
    list_before_template = "admin/list_note_client.html"

    compressed_fields = True
    warn_unsaved_form = True

    list_display = (
        "schema_name",
        "name",
        "on_trial",
        "paid_until",
        "created_on",
    )
    list_filter = ("on_trial", "created_on")
    search_fields = ("schema_name", "name")
    ordering = ("schema_name",)
    inlines = (DomainInline,)

    fieldsets = (
        ("Identity & schema", {"fields": ("schema_name", "name")}),
        ("Billing / status", {"fields": ("on_trial", "paid_until", "created_on")}),
    )
    readonly_fields = ("created_on",)


@admin.register(Domain)
class DomainAdmin(ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    autocomplete_fields = ("tenant",)

    list_display = ("domain", "tenant", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("domain", "tenant__schema_name", "tenant__name")
    ordering = ("tenant", "-is_primary", "domain")


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(DjangoUserAdmin, ModelAdmin):
    ordering = ("email",)
    autocomplete_fields = ("groups",)
    list_display = (
        "email",
        "otp_enabled",
        "is_staff",
        "is_superuser",
        "is_active",
        "created_at",
    )
    list_filter = ("otp_enabled", "is_staff", "is_superuser", "is_active")
    search_fields = ("email",)
    readonly_fields = ("created_at", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Security",
            {"fields": ("otp_enabled",)},
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )


try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin, ModelAdmin):
    compressed_fields = True
    warn_unsaved_form = True
    search_fields = ("name",)
