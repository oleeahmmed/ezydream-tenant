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

    list_display = ("WhsCode", "WhsName", "City", "Country", "Inactive", "Locked", "DropShip", "BinActivat")
    list_filter = ("Inactive", "Locked", "DropShip", "BinActivat", "Country")
    search_fields = (
        "WhsCode",
        "WhsName",
        "Location",
        "City",
        "Street",
        "StreetNo",
        "ZipCode",
        "E_Mail",
        "FederalTaxID",
    )
    ordering = ("WhsCode",)

    fieldsets = (
        (_("Identification"), {"fields": (("WhsCode", "WhsName"),), "classes": ("tab",)}),
        (
            _("Address"),
            {
                "fields": (
                    ("Street", "StreetNo", "Building", "Block"),
                    ("ZipCode", "City", "County"),
                    ("State", "Country"),
                ),
                "classes": ("tab",),
            },
        ),
        (_("Contact"), {"fields": (("Phone1", "Phone2"), ("Fax", "E_Mail"), ("FederalTaxID",)), "classes": ("tab",)}),
        (
            _("Location & status"),
            {"fields": (("Location",), ("Inactive", "Locked", "DropShip", "BinActivat")), "classes": ("tab",)},
        ),
    )
