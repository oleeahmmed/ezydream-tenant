"""Django admin for warehouse master (OWHS) — Unfold."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.erp_admin import ErpModelAdmin

from .models import OWHS


@admin.register(OWHS)
class OWHSAdmin(ErpModelAdmin):
    """Warehouse master rows."""

    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_warehouse_admin.js")

    list_display = ("WhsCode", "WhsName", "Location", "Inactive")
    list_filter = ("Inactive",)
    search_fields = ("WhsCode", "WhsName", "Location")
    ordering = ("WhsCode",)

    fieldsets = (
        (_("Identification"), {"fields": (("WhsCode", "WhsName"),), "classes": ("tab",)}),
        (_("Location & status"), {"fields": (("Location", "Inactive"),), "classes": ("tab",)}),
    )
