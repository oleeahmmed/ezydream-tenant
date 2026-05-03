"""Django admin for Purchase A/P document headers (Unfold) — tabs, multi-column rows, line inlines."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline

from apps.core.erp_admin import ErpModelAdmin

from .models import OPCH, OPDN, OPOR, OPRQ, ORPC, PCH1, PDN1, POR1, PRQ1, RPC1


class _PurchaseLineTabularInline(TabularInline):
    extra = 0
    min_num = 0
    show_change_link = False
    fk_name = "header"


class PRQ1Inline(_PurchaseLineTabularInline):
    model = PRQ1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "OpenQty",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "Currency",
        "VatGroup",
        "WhsCode",
        "LineStatus",
        "Canceled",
    )


class POR1Inline(_PurchaseLineTabularInline):
    model = POR1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "OpenQty",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "Currency",
        "VatGroup",
        "WhsCode",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class PDN1Inline(_PurchaseLineTabularInline):
    model = PDN1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "OpenQty",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "Currency",
        "VatGroup",
        "WhsCode",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class RPC1Inline(_PurchaseLineTabularInline):
    model = RPC1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "OpenQty",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "Currency",
        "VatGroup",
        "WhsCode",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class PCH1Inline(_PurchaseLineTabularInline):
    model = PCH1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "OpenQty",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "Currency",
        "VatGroup",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class _PurchaseDocAdmin(ErpModelAdmin):
    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_purchase_admin.js")

    def get_fieldsets(self, request, obj=None):
        out = [
            (_("Document"), {"fields": self._document_field_rows(obj), "classes": ("tab",)}),
        ]
        mid = self._middle_field_rows()
        if mid:
            out.append((_("Business partner / request"), {"fields": mid, "classes": ("tab",)}))
        amt = self._amount_field_rows()
        if amt:
            out.append((_("Amounts"), {"fields": amt, "classes": ("tab",)}))
        cm = self._comments_memo_field_rows()
        if cm:
            out.append((_("Comments & journal"), {"fields": cm, "classes": ("tab",)}))
        out.append((_("Status"), {"fields": self._status_field_rows(), "classes": ("tab",)}))
        return tuple(out)

    def _comments_memo_field_rows(self):
        return ()

    def _document_field_rows(self, obj):
        ext = tuple(self._document_extra())
        if obj is not None:
            rows = [("DocEntry", "DocNum")]
            if len(ext) == 2:
                rows.append((ext[0], ext[1]))
            elif len(ext) == 1:
                rows.append((ext[0],))
            return tuple(rows)
        if len(ext) >= 2:
            return (("DocNum", ext[0]), (ext[1],))
        if len(ext) == 1:
            return (("DocNum", ext[0]),)
        return (("DocNum",),)

    def _middle_field_rows(self):
        f = tuple(self._middle_fields())
        if not f:
            return ()
        if len(f) == 1:
            return (f,)
        if len(f) >= 3:
            return (f[:2], (f[2],))
        return (f,)

    def _amount_field_rows(self):
        f = tuple(self._amount_fields())
        if not f:
            return ()
        if len(f) == 1:
            return (f,)
        return (tuple(f),)

    def _status_field_rows(self):
        return (("Canceled",),)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj) or ())
        if obj is not None:
            ro.insert(0, "DocEntry")
        return tuple(dict.fromkeys(ro))

    def _document_extra(self):
        return ()

    def _middle_fields(self):
        return ()

    def _amount_fields(self):
        return ()


@admin.register(OPRQ)
class OPRQAdmin(_PurchaseDocAdmin):
    """Purchase requests."""

    inlines = (PRQ1Inline,)
    list_display = ("DocEntry", "DocNum", "Requester", "DocStatus", "DocDate", "DocDueDate", "Canceled")
    list_filter = ("DocStatus", "DocDate", "Canceled")
    search_fields = ("Requester", "DocNum")

    def _document_extra(self):
        return ("DocDate", "DocDueDate")

    def _middle_fields(self):
        return ("Requester", "NumAtCard", "CntctPrsn", "DocCur", "DocRate")

    def _comments_memo_field_rows(self):
        return (("Comments",), ("JrnlMemo",))

    def _status_field_rows(self):
        return (("DocStatus", "Handwrtten", "Printed", "Canceled"),)


@admin.register(OPOR)
class OPORAdmin(_PurchaseDocAdmin):
    """Purchase orders."""

    inlines = (POR1Inline,)
    list_display = ("DocEntry", "DocNum", "CardCode", "DocStatus", "DocDate", "DocTotal", "Canceled")
    list_filter = ("DocStatus", "DocDate", "Canceled")
    search_fields = ("CardCode", "CardName", "DocNum", "NumAtCard", "Comments")

    def _document_extra(self):
        return ("DocDate",)

    def _middle_fields(self):
        return (
            "CardCode",
            "CardName",
            "NumAtCard",
            "CntctPrsn",
            "DocCur",
            "DocRate",
            "DocDueDate",
            "TaxDate",
            "SlpCode",
            "OwnerCode",
        )

    def _comments_memo_field_rows(self):
        return (("Comments",), ("JrnlMemo",))

    def _amount_fields(self):
        return ("DocTotal", "DiscSum", "VatSum")

    def _status_field_rows(self):
        return (("DocStatus", "Handwrtten", "Printed", "Canceled"),)


@admin.register(OPDN)
class OPDNAdmin(_PurchaseDocAdmin):
    """Goods receipt PO (GRPO)."""

    inlines = (PDN1Inline,)
    list_display = ("DocEntry", "DocNum", "CardCode", "DocDate", "DocStatus", "DocTotal", "Canceled")
    list_filter = ("DocStatus", "DocDate", "Canceled")
    search_fields = ("CardCode", "CardName", "DocNum", "NumAtCard", "Comments")

    def _document_extra(self):
        return ("DocDate",)

    def _middle_fields(self):
        return (
            "CardCode",
            "CardName",
            "NumAtCard",
            "CntctPrsn",
            "DocCur",
            "DocRate",
            "DocDueDate",
            "TaxDate",
            "SlpCode",
            "OwnerCode",
        )

    def _comments_memo_field_rows(self):
        return (("Comments",), ("JrnlMemo",))

    def _amount_fields(self):
        return ("DocTotal", "DiscSum", "VatSum")

    def _status_field_rows(self):
        return (("DocStatus", "Handwrtten", "Printed", "Canceled"),)


@admin.register(ORPC)
class ORPCAdmin(_PurchaseDocAdmin):
    """Goods returns to vendor."""

    inlines = (RPC1Inline,)
    list_display = ("DocEntry", "DocNum", "CardCode", "DocDate", "DocStatus", "DocTotal", "Canceled")
    list_filter = ("DocStatus", "DocDate", "Canceled")
    search_fields = ("CardCode", "CardName", "DocNum", "NumAtCard", "Comments")

    def _document_extra(self):
        return ("DocDate",)

    def _middle_fields(self):
        return (
            "CardCode",
            "CardName",
            "NumAtCard",
            "CntctPrsn",
            "DocCur",
            "DocRate",
            "DocDueDate",
            "TaxDate",
            "SlpCode",
            "OwnerCode",
        )

    def _comments_memo_field_rows(self):
        return (("Comments",), ("JrnlMemo",))

    def _amount_fields(self):
        return ("DocTotal", "DiscSum", "VatSum")

    def _status_field_rows(self):
        return (("DocStatus", "Handwrtten", "Printed", "Canceled"),)


@admin.register(OPCH)
class OPCHAdmin(_PurchaseDocAdmin):
    """A/P invoices."""

    inlines = (PCH1Inline,)
    list_display = ("DocEntry", "DocNum", "CardCode", "DocDate", "DocTotal", "VatSum", "Canceled")
    list_filter = ("DocDate", "Canceled")
    search_fields = ("CardCode", "CardName", "DocNum", "NumAtCard", "Comments")

    def _document_extra(self):
        return ("DocDate",)

    def _middle_fields(self):
        return (
            "CardCode",
            "CardName",
            "NumAtCard",
            "CntctPrsn",
            "DocCur",
            "DocRate",
            "DocDueDate",
            "TaxDate",
            "SlpCode",
            "OwnerCode",
        )

    def _comments_memo_field_rows(self):
        return (("Comments",), ("JrnlMemo",))

    def _amount_fields(self):
        return ("DocTotal", "DiscSum", "VatSum")

    def _status_field_rows(self):
        return (("DocStatus", "Handwrtten", "Printed", "Canceled"),)
