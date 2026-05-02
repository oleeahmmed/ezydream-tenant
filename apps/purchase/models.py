"""
SAP Business One Purchase: request (OPRQ), order (OPOR), GRPO (OPDN),
goods return (ORPC), A/P invoice (OPCH).

Headers (O*) and lines use SAP names; lines use ``CompositePrimaryKey``.
``Canceled`` = Y/N soft delete (same pattern as ``apps.sales``).
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import b1_ui_labels as ui


def _doc_status(value: str) -> None:
    if value not in ("O", "C"):
        raise ValidationError({"DocStatus": "Use O (open) or C (closed)."})


def _canceled_yn(value: str) -> None:
    if value not in ("Y", "N"):
        raise ValidationError({"Canceled": "Use Y or N (SAP-style soft delete)."})


class OPRQ(models.Model):
    """OPRQ — Purchase Request header (internal)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    Requester = models.CharField(ui.REQUESTER, max_length=200, db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DUE_DATE, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OPRQ"
        verbose_name = _("Purchase request")
        verbose_name_plural = _("Purchase requests")

    def clean(self) -> None:
        _doc_status(self.DocStatus)
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PRQ1(models.Model):
    """PRQ1 — Purchase Request lines."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OPRQ,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.ITEM_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    LineStatus = models.CharField(ui.LINE_STATUS, max_length=1, default="O", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "PRQ1"
        verbose_name = _("Purchase request line")
        verbose_name_plural = _("Purchase request lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="prq1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="prq1_whscode_ix"),
        ]

    def clean(self) -> None:
        if self.LineStatus not in ("O", "C"):
            raise ValidationError({"LineStatus": "Use O (open) or C (closed)."})
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OPOR(models.Model):
    """OPOR — Purchase Order header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocTotal = models.DecimalField(
        ui.DOCUMENT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OPOR"
        verbose_name = _("Purchase order")
        verbose_name_plural = _("Purchase orders")

    def clean(self) -> None:
        _doc_status(self.DocStatus)
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class POR1(models.Model):
    """POR1 — Purchase Order lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OPOR,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "POR1"
        verbose_name = _("Purchase order line")
        verbose_name_plural = _("Purchase order lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="por1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="por1_whscode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OPDN(models.Model):
    """OPDN — Goods Receipt PO (GRPO) header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OPDN"
        verbose_name = _("Goods receipt PO")
        verbose_name_plural = _("Goods receipt POs")

    def clean(self) -> None:
        _doc_status(self.DocStatus)
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PDN1(models.Model):
    """PDN1 — GRPO lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OPDN,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "PDN1"
        verbose_name = _("GRPO line")
        verbose_name_plural = _("GRPO lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="pdn1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="pdn1_whscode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ORPC(models.Model):
    """ORPC — Goods return to vendor header (SAP-style table name in this project)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "ORPC"
        verbose_name = _("Goods return (vendor)")
        verbose_name_plural = _("Goods returns (vendor)")

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RPC1(models.Model):
    """RPC1 — Goods return lines."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        ORPC,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "RPC1"
        verbose_name = _("Goods return line")
        verbose_name_plural = _("Goods return lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="rpc1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="rpc1_whscode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OPCH(models.Model):
    """OPCH — A/P Invoice header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocTotal = models.DecimalField(
        ui.DOCUMENT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    VatSum = models.DecimalField(
        ui.TAX,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OPCH"
        verbose_name = _("A/P invoice")
        verbose_name_plural = _("A/P invoices")

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PCH1(models.Model):
    """PCH1 — A/P Invoice lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OPCH,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    LineTotal = models.DecimalField(
        ui.LINE_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "PCH1"
        verbose_name = _("A/P invoice line")
        verbose_name_plural = _("A/P invoice lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="pch1_itemcode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
