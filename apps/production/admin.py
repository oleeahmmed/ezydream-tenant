"""Django admin for Production (Unfold): BOM + production orders with line inlines."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline

from apps.core.erp_admin import ErpModelAdmin

from .models import ITT1, OITT, OWOR, WOR1


class _ProdLineTabularInline(TabularInline):
    extra = 0
    min_num = 0
    show_change_link = False
    fk_name = "header"


class ITT1Inline(_ProdLineTabularInline):
    model = ITT1
    fields = ("LineNum", "ItemCode", "Quantity", "WhsCode", "Canceled")


class WOR1Inline(_ProdLineTabularInline):
    model = WOR1
    fields = ("LineNum", "ItemCode", "PlannedQty", "IssuedQty", "WhsCode", "Canceled")


class _ProdDocMediaAdmin(ErpModelAdmin):
    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_production_admin.js")


@admin.register(OITT)
class OITTAdmin(_ProdDocMediaAdmin):
    """Bills of materials."""

    inlines = (ITT1Inline,)
    list_display = ("Code", "TreeType", "Quantity", "Canceled")
    list_filter = ("TreeType", "Canceled")
    search_fields = ("Code",)

    fieldsets = (
        (_("BOM"), {"fields": (("Code", "TreeType"), ("Quantity", "Canceled")), "classes": ("tab",)}),
    )


@admin.register(OWOR)
class OWORAdmin(_ProdDocMediaAdmin):
    """Production orders."""

    inlines = (WOR1Inline,)
    list_display = ("DocEntry", "DocNum", "ItemCode", "Status", "PostDate", "PlannedQty", "CmpltQty", "Canceled")
    list_filter = ("Status", "PostDate", "Canceled")
    search_fields = ("ItemCode", "DocNum")

    def get_fieldsets(self, request, obj=None):
        doc = ("DocNum",) if obj is None else ("DocEntry", "DocNum")
        return (
            (_("Document"), {"fields": (doc,), "classes": ("tab",)}),
            (_("Item & warehouse"), {"fields": (("ItemCode", "WhsCode"),), "classes": ("tab",)}),
            (_("Quantities & status"), {"fields": (("Status", "PlannedQty"), ("CmpltQty", "PostDate")), "classes": ("tab",)}),
            (_("Other"), {"fields": (("Canceled",),), "classes": ("tab",)}),
        )

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj) or ())
        if obj is not None:
            ro.insert(0, "DocEntry")
        return tuple(dict.fromkeys(ro))
