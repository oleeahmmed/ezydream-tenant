"""
Django admin for inventory (SAP B1-style): masters, document headers with line inlines.

Composite PK models (OITW, …) stay off admin; use the REST API.
"""

from django.contrib import admin
from django.contrib.admin import display
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline

from apps.core.erp_admin import ErpModelAdmin

from .models import IGE1, IGN1, INC1, OINC, OIGE, OIGN, OITB, OITM, OINM, OUOM, OWTR, OWTQ, WTQ1, WTR1


class _InvLineTabularInline(TabularInline):
    extra = 0
    min_num = 0
    show_change_link = False
    fk_name = "header"


class WTQ1Inline(_InvLineTabularInline):
    model = WTQ1
    fields = (
        "LineNum",
        "ItemCode",
        "Quantity",
        "OpenQty",
        "Price",
        "FromWhsCod",
        "WhsCode",
        "LineStatus",
        "TargetType",
        "TrgetEntry",
        "BaseRef",
        "BaseType",
        "BaseEntry",
        "Canceled",
    )


class WTR1Inline(_InvLineTabularInline):
    model = WTR1
    fields = ("LineNum", "ItemCode", "Quantity", "WhsCode", "Price", "Canceled")


class IGN1Inline(_InvLineTabularInline):
    model = IGN1
    fields = ("LineNum", "ItemCode", "Quantity", "WhsCode", "Price", "BaseType", "BaseEntry", "BaseLine", "Canceled")


class IGE1Inline(_InvLineTabularInline):
    model = IGE1
    fields = (
        "LineNum",
        "ItemCode",
        "Quantity",
        "WhsCode",
        "Account",
        "Price",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class INC1Inline(_InvLineTabularInline):
    model = INC1
    fields = ("LineNum", "ItemCode", "WhsCode", "InQty", "OutQty", "Difference", "Price", "Canceled")


class _InventoryDocAdmin(ErpModelAdmin):
    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_inventory_admin.js")

    def get_fieldsets(self, request, obj=None):
        return (
            (_("Document"), {"fields": self._document_field_rows(obj), "classes": ("tab",)}),
            (_("Dates & parties"), {"fields": self._dates_parties_field_rows(), "classes": ("tab",)}),
            (_("Other"), {"fields": self._other_field_rows(), "classes": ("tab",)}),
        )

    def _document_field_rows(self, obj):
        if obj is not None:
            return (("DocEntry", "DocNum"),)
        return (("DocNum",),)

    def _dates_parties_field_rows(self):
        return ()

    def _other_field_rows(self):
        return (("Canceled",),)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj) or ())
        if obj is not None:
            ro.insert(0, "DocEntry")
        return tuple(dict.fromkeys(ro))


@admin.register(OITB)
class OITBAdmin(ErpModelAdmin):
    """Item groups master."""

    list_display = ("ItmsGrpCod", "ItmsGrpNam", "Canceled")
    list_filter = ("Canceled",)
    search_fields = ("ItmsGrpNam",)
    ordering = ("ItmsGrpCod",)

    fieldsets = (
        (_("Group"), {"fields": (("ItmsGrpCod", "ItmsGrpNam"), "Canceled"), "classes": ("tab",)}),
    )


@admin.register(OITM)
class OITMAdmin(ErpModelAdmin):
    """Item master (stock and group flags)."""

    list_display = (
        "ItemCode",
        "ItemName",
        "itms_grp_display",
        "InvntItem",
        "OnHand",
        "ByWh",
        "ValidFor",
    )
    list_filter = ("InvntItem", "ByWh", "ValidFor")
    search_fields = ("ItemCode", "ItemName")
    ordering = ("ItemCode",)
    autocomplete_fields = ("ItmsGrpCod",)

    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_inventory_admin.js")

    fieldsets = (
        (_("Item"), {"fields": (("ItemCode", "ItemName"), "ItmsGrpCod"), "classes": ("tab",)}),
        (
            _("Stock & flags"),
            {
                "fields": (
                    ("InvntItem", "ByWh", "ValidFor"),
                    ("OnHand", "IsCommited", "OnOrder"),
                ),
                "classes": ("tab",),
            },
        ),
    )

    @display(description=_("Item group"), ordering="ItmsGrpCod_id")
    def itms_grp_display(self, obj):
        grp = getattr(obj, "ItmsGrpCod", None)
        if grp is None:
            return "—"
        return f"{grp.pk} — {grp.ItmsGrpNam}"


@admin.register(OUOM)
class OUOMAdmin(ErpModelAdmin):
    """Units of measure."""

    list_display = ("UomEntry", "UomCode", "UomName", "Locked", "DataSource")
    list_filter = ("Locked", "DataSource")
    search_fields = ("UomCode", "UomName")
    ordering = ("UomCode",)

    fieldsets = (
        (_("UoM"), {"fields": (("UomCode", "UomName"),), "classes": ("tab",)}),
        (_("System"), {"fields": (("Locked", "DataSource"),), "classes": ("tab",)}),
    )


@admin.register(OWTQ)
class OWTQAdmin(_InventoryDocAdmin):
    """Inventory transfer request headers."""

    inlines = (WTQ1Inline,)
    list_display = ("DocEntry", "DocNum", "DocDate", "Filler", "Canceled")
    list_filter = ("DocDate", "Canceled")
    search_fields = ("Filler", "Comments")

    def _dates_parties_field_rows(self):
        return (("DocDate", "Filler"), ("Comments",))


@admin.register(OWTR)
class OWTRAdmin(_InventoryDocAdmin):
    """Inventory transfer headers."""

    inlines = (WTR1Inline,)
    list_display = ("DocEntry", "DocNum", "DocDate", "Filler", "Canceled")
    list_filter = ("DocDate", "Canceled")
    search_fields = ("Filler", "Comments")

    def _dates_parties_field_rows(self):
        return (("DocDate", "Filler"), ("Comments",))


@admin.register(OIGN)
class OIGNAdmin(_InventoryDocAdmin):
    """Goods receipt headers."""

    inlines = (IGN1Inline,)
    list_display = ("DocEntry", "DocNum", "DocDate", "Canceled")
    list_filter = ("DocDate", "Canceled")
    search_fields = ("Comments",)

    def _dates_parties_field_rows(self):
        return (("DocDate",), ("Comments",))


@admin.register(OIGE)
class OIGEAdmin(_InventoryDocAdmin):
    """Goods issue headers."""

    inlines = (IGE1Inline,)
    list_display = ("DocEntry", "DocNum", "DocDate", "Canceled")
    list_filter = ("DocDate", "Canceled")
    search_fields = ("Comments",)

    def _dates_parties_field_rows(self):
        return (("DocDate",), ("Comments",))


@admin.register(OINC)
class OINCAdmin(_InventoryDocAdmin):
    """Inventory posting (counting) headers."""

    inlines = (INC1Inline,)
    list_display = ("DocEntry", "DocNum", "CountDate", "Canceled")
    list_filter = ("CountDate", "Canceled")

    def _document_field_rows(self, obj):
        if obj is not None:
            return (("DocEntry", "DocNum"), ("CountDate",))
        return (("DocNum", "CountDate"),)


@admin.register(OINM)
class OINMAdmin(ErpModelAdmin):
    """Stock ledger / transaction log."""

    list_display = ("TransNum", "TransType", "ItemCode", "Warehouse", "InQty", "OutQty", "DocTime", "Canceled")
    list_filter = ("TransType", "Canceled", "DocTime")
    search_fields = ("ItemCode", "Warehouse", "BASE_REF")
    date_hierarchy = "DocTime"
    ordering = ("-TransNum",)
    readonly_fields = (
        "TransNum",
        "TransType",
        "ItemCode",
        "Warehouse",
        "InQty",
        "OutQty",
        "Price",
        "BASE_REF",
        "DocTime",
        "Canceled",
    )

    fieldsets = (
        (_("Transaction"), {"fields": (("TransNum", "TransType"), "DocTime"), "classes": ("tab",)}),
        (_("Item & warehouse"), {"fields": (("ItemCode", "Warehouse"),), "classes": ("tab",)}),
        (_("Quantities & value"), {"fields": (("InQty", "OutQty"), "Price"), "classes": ("tab",)}),
        (_("Reference"), {"fields": (("BASE_REF", "Canceled"),), "classes": ("tab",)}),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
