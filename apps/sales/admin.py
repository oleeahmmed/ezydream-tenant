"""Django admin for Sales A/R document headers (Unfold) with tabular line inlines."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import TabularInline

from apps.core.erp_admin import ErpModelAdmin

from .models import DLN1, INV1, ODLN, OINV, OQUT, ORDN, ORDR, QUT1, RDN1, RDR1


class _SalesLineTabularInline(TabularInline):
    """SAP-style document lines; shown below the header (no separate Unfold tab)."""

    extra = 0
    min_num = 0
    show_change_link = False
    fk_name = "header"


class QUT1Inline(_SalesLineTabularInline):
    model = QUT1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "Price",
        "DiscPrcnt",
        "WhsCode",
        "LineTotal",
        "Canceled",
    )


class RDR1Inline(_SalesLineTabularInline):
    model = RDR1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "Price",
        "DiscPrcnt",
        "WhsCode",
        "LineTotal",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class DLN1Inline(_SalesLineTabularInline):
    model = DLN1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "WhsCode",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class RDN1Inline(_SalesLineTabularInline):
    model = RDN1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "WhsCode",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class INV1Inline(_SalesLineTabularInline):
    model = INV1
    fields = (
        "LineNum",
        "ItemCode",
        "Dscription",
        "Quantity",
        "Price",
        "DiscPrcnt",
        "LineTotal",
        "WhsCode",
        "BaseType",
        "BaseEntry",
        "BaseLine",
        "Canceled",
    )


class _SalesDocAdmin(ErpModelAdmin):
    """DocEntry PK: header in Unfold tabs (multi-column rows); lines stay below inlines."""

    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_sales_admin.js")

    def get_fieldsets(self, request, obj=None):
        out = [
            (_("Document"), {"fields": self._document_field_rows(obj), "classes": ("tab",)}),
            (_("Business partner"), {"fields": self._bp_field_rows(), "classes": ("tab",)}),
        ]
        amt = self._amount_field_rows()
        if amt:
            out.append((_("Amounts & tax"), {"fields": amt, "classes": ("tab",)}))
        out.append((_("Status"), {"fields": self._status_field_rows(), "classes": ("tab",)}))
        return tuple(out)

    def _document_field_rows(self, obj):
        """Two-column rows for document number, status, dates (add vs change)."""
        ext = tuple(self._document_extra())
        if obj is not None:
            rows: list[tuple[str, ...]] = [("DocEntry", "DocNum")]
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

    def _bp_field_rows(self):
        f = tuple(self._bp_fields())
        if len(f) >= 3:
            return (f[:2], (f[2],))
        if len(f) == 2:
            return (f,)
        if len(f) == 1:
            return (f,)
        return ()

    def _amount_field_rows(self):
        f = tuple(self._amount_fields())
        if not f:
            return ()
        if len(f) == 1:
            return (f,)
        return (tuple(f),)

    @staticmethod
    def _status_field_rows():
        return (("Canceled",),)

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj) or ())
        if obj is not None:
            ro.insert(0, "DocEntry")
        return tuple(dict.fromkeys(ro))

    def _document_extra(self):
        return ()

    def _bp_fields(self):
        return ("CardCode", "CardName")

    def _amount_fields(self):
        return ()


@admin.register(OQUT)
class OQUTAdmin(_SalesDocAdmin):
    """Sales quotations."""

    inlines = (QUT1Inline,)
    list_display = (
        "DocEntry",
        "DocNum",
        "CardCode",
        "DocStatus",
        "DocDate",
        "DocDueDate",
        "DocTotal",
        "Canceled",
    )
    list_filter = ("DocStatus", "DocDate", "DocDueDate", "Canceled")
    search_fields = ("CardCode", "CardName", "NumAtCard", "DocNum", "CntctPrsn", "Comments")

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            doc_rows = (
                ("DocEntry", "DocNum"),
                ("DocStatus", "DocDate"),
                ("DocDueDate", "TaxDate"),
            )
        else:
            doc_rows = (
                ("DocNum", "DocStatus"),
                ("DocDate", "DocDueDate"),
                ("TaxDate",),
            )
        bp_rows = (
            ("CardCode", "CardName"),
            ("CntctPrsn", "DocCur"),
            ("NumAtCard",),
        )
        totals_rows = (("DocTotal", "VatSum"), ("DiscSum",))
        other_rows = (("Comments",), ("SlpCode", "OwnerCode"))
        status_rows = (("Canceled",),)
        return (
            (_("Document"), {"fields": doc_rows, "classes": ("tab",)}),
            (_("Customer / commercial"), {"fields": bp_rows, "classes": ("tab",)}),
            (_("Totals"), {"fields": totals_rows, "classes": ("tab",)}),
            (_("Remarks & ownership"), {"fields": other_rows, "classes": ("tab",)}),
            (_("Status"), {"fields": status_rows, "classes": ("tab",)}),
        )


@admin.register(ORDR)
class ORDRAdmin(_SalesDocAdmin):
    """Sales order — extended ORDR/RDR1 fields closer to SAP B1 (dates, currency, totals, lines)."""

    inlines = (RDR1Inline,)
    list_display = (
        "DocEntry",
        "DocNum",
        "CardCode",
        "DocStatus",
        "DocDate",
        "DocDueDate",
        "DocTotal",
        "Canceled",
    )
    list_filter = ("DocStatus", "DocDate", "DocDueDate", "Canceled")
    search_fields = ("CardCode", "CardName", "NumAtCard", "DocNum", "CntctPrsn", "Comments")

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            doc_rows = (
                ("DocEntry", "DocNum"),
                ("DocStatus", "DocDate"),
                ("DocDueDate", "TaxDate"),
            )
        else:
            doc_rows = (
                ("DocNum", "DocStatus"),
                ("DocDate", "DocDueDate"),
                ("TaxDate",),
            )
        bp_rows = (
            ("CardCode", "CardName"),
            ("CntctPrsn", "DocCur"),
            ("NumAtCard",),
        )
        totals_rows = (("DocTotal", "VatSum"), ("DiscSum",))
        other_rows = (("Comments",), ("SlpCode", "OwnerCode"))
        status_rows = (("Canceled",),)
        return (
            (_("Document"), {"fields": doc_rows, "classes": ("tab",)}),
            (_("Customer / commercial"), {"fields": bp_rows, "classes": ("tab",)}),
            (_("Totals"), {"fields": totals_rows, "classes": ("tab",)}),
            (_("Remarks & ownership"), {"fields": other_rows, "classes": ("tab",)}),
            (_("Status"), {"fields": status_rows, "classes": ("tab",)}),
        )


@admin.register(ODLN)
class ODLNAdmin(_SalesDocAdmin):
    """Deliveries."""

    inlines = (DLN1Inline,)
    list_display = (
        "DocEntry",
        "DocNum",
        "CardCode",
        "DocStatus",
        "DocDate",
        "DocDueDate",
        "DocTotal",
        "Canceled",
    )
    list_filter = ("DocStatus", "DocDate", "DocDueDate", "Canceled")
    search_fields = ("CardCode", "CardName", "NumAtCard", "DocNum", "CntctPrsn", "Comments")

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            doc_rows = (
                ("DocEntry", "DocNum"),
                ("DocStatus", "DocDate"),
                ("DocDueDate", "TaxDate"),
            )
        else:
            doc_rows = (
                ("DocNum", "DocStatus"),
                ("DocDate", "DocDueDate"),
                ("TaxDate",),
            )
        bp_rows = (
            ("CardCode", "CardName"),
            ("CntctPrsn", "DocCur"),
            ("NumAtCard",),
        )
        totals_rows = (("DocTotal", "VatSum"), ("DiscSum",))
        other_rows = (("Comments",), ("SlpCode", "OwnerCode"))
        status_rows = (("Canceled",),)
        return (
            (_("Document"), {"fields": doc_rows, "classes": ("tab",)}),
            (_("Customer / commercial"), {"fields": bp_rows, "classes": ("tab",)}),
            (_("Totals"), {"fields": totals_rows, "classes": ("tab",)}),
            (_("Remarks & ownership"), {"fields": other_rows, "classes": ("tab",)}),
            (_("Status"), {"fields": status_rows, "classes": ("tab",)}),
        )


@admin.register(ORDN)
class ORDNAdmin(_SalesDocAdmin):
    """Returns."""

    inlines = (RDN1Inline,)
    list_display = (
        "DocEntry",
        "DocNum",
        "CardCode",
        "DocStatus",
        "DocDate",
        "DocDueDate",
        "DocTotal",
        "Canceled",
    )
    list_filter = ("DocStatus", "DocDate", "DocDueDate", "Canceled")
    search_fields = ("CardCode", "CardName", "NumAtCard", "DocNum", "CntctPrsn", "Comments")

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            doc_rows = (
                ("DocEntry", "DocNum"),
                ("DocStatus", "DocDate"),
                ("DocDueDate", "TaxDate"),
            )
        else:
            doc_rows = (
                ("DocNum", "DocStatus"),
                ("DocDate", "DocDueDate"),
                ("TaxDate",),
            )
        bp_rows = (
            ("CardCode", "CardName"),
            ("CntctPrsn", "DocCur"),
            ("NumAtCard",),
        )
        totals_rows = (("DocTotal", "VatSum"), ("DiscSum",))
        other_rows = (("Comments",), ("SlpCode", "OwnerCode"))
        status_rows = (("Canceled",),)
        return (
            (_("Document"), {"fields": doc_rows, "classes": ("tab",)}),
            (_("Customer / commercial"), {"fields": bp_rows, "classes": ("tab",)}),
            (_("Totals"), {"fields": totals_rows, "classes": ("tab",)}),
            (_("Remarks & ownership"), {"fields": other_rows, "classes": ("tab",)}),
            (_("Status"), {"fields": status_rows, "classes": ("tab",)}),
        )


@admin.register(OINV)
class OINVAdmin(_SalesDocAdmin):
    """A/R invoices."""

    inlines = (INV1Inline,)
    list_display = (
        "DocEntry",
        "DocNum",
        "CardCode",
        "DocDate",
        "DocDueDate",
        "DocTotal",
        "VatSum",
        "DiscSum",
        "Canceled",
    )
    list_filter = ("DocDate", "DocDueDate", "Canceled")
    search_fields = ("CardCode", "CardName", "NumAtCard", "DocNum", "CntctPrsn", "Comments")

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            doc_rows = (
                ("DocEntry", "DocNum"),
                ("DocDate", "DocDueDate"),
                ("TaxDate",),
            )
        else:
            doc_rows = (
                ("DocNum",),
                ("DocDate", "DocDueDate"),
                ("TaxDate",),
            )
        bp_rows = (
            ("CardCode", "CardName"),
            ("CntctPrsn", "DocCur"),
            ("NumAtCard",),
        )
        totals_rows = (("DocTotal", "VatSum"), ("DiscSum",))
        other_rows = (("Comments",), ("SlpCode", "OwnerCode"))
        status_rows = (("Canceled",),)
        return (
            (_("Document"), {"fields": doc_rows, "classes": ("tab",)}),
            (_("Customer / commercial"), {"fields": bp_rows, "classes": ("tab",)}),
            (_("Totals"), {"fields": totals_rows, "classes": ("tab",)}),
            (_("Remarks & ownership"), {"fields": other_rows, "classes": ("tab",)}),
            (_("Status"), {"fields": status_rows, "classes": ("tab",)}),
        )
