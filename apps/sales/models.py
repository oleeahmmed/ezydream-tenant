"""
SAP Business One Sales A/R: quotations, orders, deliveries, returns, invoices.

Headers (O*) and lines (*1) use SAP table and column names. Lines use
``CompositePrimaryKey`` (DocEntry + LineNum) like inventory documents.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import b1_ui_labels as ui


def _doc_status(value: str) -> None:
    if value not in ("O", "C"):
        raise ValidationError({"DocStatus": "Use O (open) or C (closed)."})


def _canceled_yn(value: str) -> None:
    if value not in ("Y", "N"):
        raise ValidationError({"Canceled": "Use Y or N (SAP-style soft delete)."})


class OQUT(models.Model):
    """OQUT — Sales Quotation header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DELIVERY_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
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
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OQUT"
        verbose_name = _("Sales quotation")
        verbose_name_plural = _("Sales quotations")

    def clean(self) -> None:
        _doc_status(self.DocStatus)
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class QUT1(models.Model):
    """QUT1 — Sales Quotation lines (SAP B1). ``Dscription`` = SAP spelling."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OQUT,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.ITEM_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    DiscPrcnt = models.DecimalField(
        ui.DISCOUNT_PCT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    LineTotal = models.DecimalField(
        ui.LINE_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "QUT1"
        verbose_name = _("Sales quotation line")
        verbose_name_plural = _("Sales quotation lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="qut1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="qut1_whscode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ORDR(models.Model):
    """ORDR — Sales Order header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DELIVERY_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
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
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "ORDR"
        verbose_name = _("Sales order")
        verbose_name_plural = _("Sales orders")

    def clean(self) -> None:
        _doc_status(self.DocStatus)
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RDR1(models.Model):
    """RDR1 — Sales Order lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        ORDR,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.ITEM_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    DiscPrcnt = models.DecimalField(
        ui.DISCOUNT_PCT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    LineTotal = models.DecimalField(
        ui.LINE_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "RDR1"
        verbose_name = _("Sales order line")
        verbose_name_plural = _("Sales order lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="rdr1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="rdr1_whscode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ODLN(models.Model):
    """ODLN — Delivery header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DELIVERY_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
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
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "ODLN"
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")

    def clean(self) -> None:
        _doc_status(self.DocStatus)
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class DLN1(models.Model):
    """DLN1 — Delivery lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        ODLN,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.ITEM_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    DiscPrcnt = models.DecimalField(
        ui.DISCOUNT_PCT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    LineTotal = models.DecimalField(
        ui.LINE_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "DLN1"
        verbose_name = _("Delivery line")
        verbose_name_plural = _("Delivery lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="dln1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="dln1_whscode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ORDN(models.Model):
    """ORDN — Return header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DELIVERY_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
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
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "ORDN"
        verbose_name = _("Return")
        verbose_name_plural = _("Returns")

    def clean(self) -> None:
        _doc_status(self.DocStatus)
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class RDN1(models.Model):
    """RDN1 — Return lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        ORDN,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.ITEM_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    DiscPrcnt = models.DecimalField(
        ui.DISCOUNT_PCT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    LineTotal = models.DecimalField(
        ui.LINE_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "RDN1"
        verbose_name = _("Return line")
        verbose_name_plural = _("Return lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="rdn1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="rdn1_whscode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OINV(models.Model):
    """OINV — A/R Invoice header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DELIVERY_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
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
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OINV"
        verbose_name = _("A/R invoice")
        verbose_name_plural = _("A/R invoices")

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class INV1(models.Model):
    """INV1 — A/R Invoice lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OINV,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.ITEM_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    DiscPrcnt = models.DecimalField(
        ui.DISCOUNT_PCT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    LineTotal = models.DecimalField(
        ui.LINE_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, blank=True, default="", db_index=True)
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "INV1"
        verbose_name = _("A/R invoice line")
        verbose_name_plural = _("A/R invoice lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="inv1_itemcode_ix"),
        ]

    def clean(self) -> None:
        _canceled_yn(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
