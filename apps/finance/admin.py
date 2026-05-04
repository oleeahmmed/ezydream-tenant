"""
Django admin for Finance (SAP B1–style headers / masters).

Line tables with ``CompositePrimaryKey`` (JDT1, RCT1, VPM1, BGT1, ITL1) are not registered in Django admin
(Django does not support composite PK models in admin). Use Bolt API ``/api/finance/…`` for those lines.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.erp_admin import ErpModelAdmin

from .models import (
    AAC1,
    OAFR,
    OACD,
    OADM,
    OACT,
    OAGS,
    OBGT,
    OCTD,
    ODRN,
    OFAV,
    OIBT,
    OITL,
    OJDT,
    OFPR,
    OPRC,
    ORCT,
    OSTC,
    OVPM,
    OVTG,
)


class _FinanceErpAdmin(ErpModelAdmin):
    """Loads shared autocomplete for G/L code CharFields (session JSON, not Bolt JWT)."""

    class Media:
        js = ("admin/js/core/erp_ac_common.js", "admin/js/erp_finance_admin.js")


@admin.register(OACT)
class OACTAdmin(_FinanceErpAdmin):
    list_display = ("AcctCode", "AcctName", "GroupMask", "FatherNum", "Postable", "LocCash", "CurrTotal")
    list_filter = ("GroupMask", "Postable", "LocCash")
    search_fields = ("AcctCode", "AcctName", "FatherNum")
    ordering = ("AcctCode",)

    fieldsets = (
        (_("Account"), {"fields": (("AcctCode", "AcctName"), ("FatherNum",)), "classes": ("tab",)}),
        (_("Classification"), {"fields": (("GroupMask", "Postable", "LocCash", "AcctFixed"),), "classes": ("tab",)}),
        (_("Validity & export"), {"fields": (("ValidFor", "Frozen"), ("Levels", "ExportCode")), "classes": ("tab",)}),
        (_("Balance"), {"fields": (("CurrTotal",),), "classes": ("tab",)}),
    )


@admin.register(OPRC)
class OPRCAdmin(_FinanceErpAdmin):
    list_display = ("PrcCode", "PrcName", "DimCode", "Active")
    list_filter = ("DimCode", "Active")
    search_fields = ("PrcCode", "PrcName")
    ordering = ("PrcCode",)

    fieldsets = (
        (_("Center"), {"fields": (("PrcCode", "PrcName"),), "classes": ("tab",)}),
        (_("Dimension & status"), {"fields": (("DimCode", "Active", "PrcFather"),), "classes": ("tab",)}),
    )


@admin.register(OJDT)
class OJDTAdmin(_FinanceErpAdmin):
    list_display = ("TransId", "RefDate", "TransType", "BaseRef")
    list_filter = ("RefDate", "TransType")
    search_fields = ("BaseRef", "Memo")

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (_("Document"), {"fields": (("RefDate", "TransType"), "BaseRef"), "classes": ("tab",)}),
                (_("References & project"), {"fields": (("Ref1", "Ref2"), ("DueDate", "TransCode"), ("Project",)), "classes": ("tab",)}),
                (_("Memo"), {"fields": (("Memo",),), "classes": ("tab",)}),
            )
        return (
            (_("Document"), {"fields": (("TransId", "RefDate"), ("TransType", "BaseRef")), "classes": ("tab",)}),
            (_("References & project"), {"fields": (("Ref1", "Ref2"), ("DueDate", "TransCode"), ("Project",)), "classes": ("tab",)}),
            (_("Memo"), {"fields": (("Memo",),), "classes": ("tab",)}),
        )

    def get_readonly_fields(self, request, obj=None):
        return ("TransId",) if obj else ()


@admin.register(ORCT)
class ORCTAdmin(_FinanceErpAdmin):
    list_display = ("DocEntry", "CardCode", "DocDate", "DocTotal", "CashSum", "DocStatus")
    list_filter = ("DocDate", "DocStatus")
    search_fields = ("CardCode", "CardName")

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (_("Document & BP"), {"fields": (("DocDate", "CardCode"), ("CardName",)), "classes": ("tab",)}),
                (_("Status & transfer"), {"fields": (("DocStatus", "TrsfrAcct"), ("CheckSum",)), "classes": ("tab",)}),
                (_("Accounts & amounts"), {"fields": (("CashAcct", "CheckAcct"), ("DocTotal", "CashSum")), "classes": ("tab",)}),
                (_("Comments & journal"), {"fields": (("Comments",), ("JrnlMemo",)), "classes": ("tab",)}),
            )
        return (
            (_("Document"), {"fields": (("DocEntry", "DocDate"), ("CardCode", "CardName")), "classes": ("tab",)}),
            (_("Status & transfer"), {"fields": (("DocStatus", "TrsfrAcct"), ("CheckSum",)), "classes": ("tab",)}),
            (_("Accounts & amounts"), {"fields": (("CashAcct", "CheckAcct"), ("DocTotal", "CashSum")), "classes": ("tab",)}),
            (_("Comments & journal"), {"fields": (("Comments",), ("JrnlMemo",)), "classes": ("tab",)}),
        )

    def get_readonly_fields(self, request, obj=None):
        return ("DocEntry",) if obj else ()


@admin.register(OVPM)
class OVPMAdmin(_FinanceErpAdmin):
    list_display = ("DocEntry", "CardCode", "DocDate", "DocTotal", "CashSum", "TrsfrSum", "DocStatus")
    list_filter = ("DocDate", "DocStatus")
    search_fields = ("CardCode", "CardName", "Comments")

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (_("Document & BP"), {"fields": (("DocDate", "CardCode"), ("CardName",)), "classes": ("tab",)}),
                (_("Status & transfer"), {"fields": (("DocStatus", "TrsfrAcct"),), "classes": ("tab",)}),
                (_("Bank & amounts"), {"fields": (("BankAcct",), ("CashSum", "TrsfrSum", "DocTotal")), "classes": ("tab",)}),
                (_("Comments & journal"), {"fields": (("Comments",), ("JrnlMemo",)), "classes": ("tab",)}),
            )
        return (
            (_("Document"), {"fields": (("DocEntry", "DocDate"), ("CardCode", "CardName")), "classes": ("tab",)}),
            (_("Status & transfer"), {"fields": (("DocStatus", "TrsfrAcct"),), "classes": ("tab",)}),
            (_("Bank & amounts"), {"fields": (("BankAcct",), ("CashSum", "TrsfrSum", "DocTotal")), "classes": ("tab",)}),
            (_("Comments & journal"), {"fields": (("Comments",), ("JrnlMemo",)), "classes": ("tab",)}),
        )

    def get_readonly_fields(self, request, obj=None):
        return ("DocEntry",) if obj else ()


@admin.register(OSTC)
class OSTCAdmin(_FinanceErpAdmin):
    list_display = ("Code", "Name", "Rate", "Account", "ValidFor", "Frozen")
    list_filter = ("ValidFor", "Frozen")
    search_fields = ("Code", "Name", "Account")
    ordering = ("Code",)

    fieldsets = (
        (_("Tax code"), {"fields": (("Code", "Name", "Rate"),), "classes": ("tab",)}),
        (_("G/L link & flags"), {"fields": (("Account",), ("ValidFor", "Frozen")), "classes": ("tab",)}),
    )


@admin.register(OFPR)
class OFPRAdmin(_FinanceErpAdmin):
    list_display = ("AbsEntry", "PeriodCode", "F_RefDate", "T_RefDate", "PeriodStat")
    list_filter = ("PeriodStat",)
    search_fields = ("PeriodCode",)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (
                (_("Period"), {"fields": (("PeriodCode", "PeriodStat"), ("F_RefDate", "T_RefDate")), "classes": ("tab",)}),
            )
        return (
            (_("Period"), {"fields": (("AbsEntry", "PeriodCode"), ("F_RefDate", "T_RefDate"), "PeriodStat"), "classes": ("tab",)}),
        )

    def get_readonly_fields(self, request, obj=None):
        return ("AbsEntry",) if obj else ()


@admin.register(OBGT)
class OBGTAdmin(_FinanceErpAdmin):
    list_display = ("AcctCode", "BudgTotal")
    search_fields = ("AcctCode__AcctCode", "AcctCode__AcctName")
    autocomplete_fields = ("AcctCode",)

    fieldsets = (
        (_("G/L account"), {"fields": (("AcctCode",),), "classes": ("tab",)}),
        (_("Budget"), {"fields": (("BudgTotal",),), "classes": ("tab",)}),
    )

    def get_readonly_fields(self, request, obj=None):
        return ("AcctCode",) if obj else ()


@admin.register(OACD)
class OACDAdmin(admin.ModelAdmin):
    list_display = ("AbsId", "Name")


@admin.register(OADM)
class OADMAdmin(admin.ModelAdmin):
    list_display = ("AbsEntry", "CompnyName", "MainCurncy")


@admin.register(OAGS)
class OAGSAdmin(admin.ModelAdmin):
    list_display = ("GroupCode", "GroupName")


@admin.register(OCTD)
class OCTDAdmin(admin.ModelAdmin):
    list_display = ("CreditCard", "CardName")


@admin.register(OVTG)
class OVTGAdmin(admin.ModelAdmin):
    list_display = ("Code", "Name", "Rate")


@admin.register(OFAV)
class OFAVAdmin(admin.ModelAdmin):
    list_display = ("AbsEntry", "AssetCode", "CardCode")


@admin.register(OAFR)
class OAFRAdmin(admin.ModelAdmin):
    list_display = ("AbsEntry", "AssetCode", "PostDate")


@admin.register(AAC1)
class AAC1Admin(admin.ModelAdmin):
    list_display = ("Id", "ClassId", "AreaId")


@admin.register(ODRN)
class ODRNAdmin(admin.ModelAdmin):
    list_display = ("DocEntry", "F_RefDate", "T_RefDate", "Memo")


@admin.register(OITL)
class OITLAdmin(admin.ModelAdmin):
    list_display = ("ReconNum", "CardCode", "ReconDate")


@admin.register(OIBT)
class OIBTAdmin(admin.ModelAdmin):
    list_display = ("DocEntry", "TrnsfrDate", "TrnsfrSum", "Memo")
