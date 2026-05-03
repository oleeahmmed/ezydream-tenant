"""Django admin for business partners (OCRG, OCRD, CRD1) — Unfold."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline

from apps.core.erp_admin import ErpModelAdmin

from .models import CRD1, OCRD, OCRG


class CRD1Inline(TabularInline):
    model = CRD1
    fk_name = "header"
    extra = 0
    min_num = 0
    show_change_link = False
    fields = (
        "Address",
        "AdresType",
        "Street",
        "Block",
        "Building",
        "City",
        "County",
        "ZipCode",
        "Country",
        "State",
        "Canceled",
    )


@admin.register(OCRG)
class OCRGAdmin(ErpModelAdmin):
    """BP groups (OCRG)."""

    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_businesspartner_admin.js")

    list_display = ("GroupCode", "GroupName", "GroupType", "Canceled")
    list_filter = ("GroupType", "Canceled")
    search_fields = ("GroupName",)
    ordering = ("GroupCode",)

    fieldsets = (
        (_("Group"), {"fields": (("GroupCode", "GroupName", "GroupType"),), "classes": ("tab",)}),
        (_("Status"), {"fields": (("Canceled",),), "classes": ("tab",)}),
    )


@admin.register(OCRD)
class OCRDAdmin(ErpModelAdmin):
    """Business partner master (OCRD) with addresses (CRD1)."""

    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_businesspartner_admin.js")

    inlines = (CRD1Inline,)
    list_display = ("CardCode", "CardName", "CardType", "GroupCode", "ValidFor", "Frozen", "Canceled")
    list_filter = ("CardType", "ValidFor", "Frozen", "Canceled")
    search_fields = ("CardCode", "CardName", "CntctPrsn", "E_Mail", "LicTradNum")
    ordering = ("CardCode",)
    autocomplete_fields = ("GroupCode",)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj) or ())
        if obj is not None:
            ro.insert(0, "CardCode")
        return tuple(dict.fromkeys(ro))

    def get_fieldsets(self, request, obj=None):
        return (
            (_("Identification"), {"fields": (("CardCode", "CardName", "CardType"), ("GroupCode",)), "classes": ("tab",)}),
            (_("Contact"), {"fields": (("CntctPrsn",), ("Phone1", "Phone2"), ("Cellular", "Fax"), ("E_Mail", "Website")), "classes": ("tab",)}),
            (_("Names & tax"), {"fields": (("CardFName",), ("LicTradNum",)), "classes": ("tab",)}),
            (_("Financial"), {"fields": (("CreditLine", "DebtLine"), ("Balance",), ("OrdersBal", "DNotesBal"), ("Currency", "PayTermsGrpCode")), "classes": ("tab",)}),
            (_("Defaults"), {"fields": (("DfltWhs",), ("ShipToDef", "BillToDef"), ("SlpCode",)), "classes": ("tab",)}),
            (_("Remarks & status"), {"fields": (("Comments",), ("ValidFor", "Frozen", "Canceled")), "classes": ("tab",)}),
        )
