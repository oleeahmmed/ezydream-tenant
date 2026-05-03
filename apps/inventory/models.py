"""
SAP Business One–style inventory: masters (OITB, OITM, OITW, OUOM), documents,
inventory transfer request (OWTQ, WTQ1), and OINM.

Warehouse master OWHS lives in ``apps.warehouse``; this app uses WhsCode / ItemCode
strings on lines and OITW per B1 (no extra Django relations beyond OITM→OITB).
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core import b1_ui_labels as ui


def validate_yes_no_char(value: str) -> None:
    """Raise if the value is not SAP-style Y/N."""
    if value not in ("Y", "N"):
        raise ValidationError("Use Y or N.")


def _doc_status_oc(value: str) -> None:
    if value not in ("O", "C"):
        raise ValidationError({"DocStatus": "Use O (open) or C (closed)."})


class OITB(models.Model):
    """OITB — Item Groups (SAP B1); referenced by OITM.ItmsGrpCod."""

    ItmsGrpCod = models.PositiveSmallIntegerField(ui.ITEM_GROUP, primary_key=True)
    ItmsGrpNam = models.CharField(ui.ITEM_GROUP_NAME, max_length=200, db_index=True)
    Locked = models.CharField(ui.ITEM_GROUP_LOCKED, max_length=1, default="N", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OITB"
        verbose_name = _("Item group")
        verbose_name_plural = _("Item groups")

    def __str__(self) -> str:
        return f"{self.ItmsGrpCod} — {self.ItmsGrpNam}"

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)
        validate_yes_no_char(self.Locked)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OITM(models.Model):
    """OITM — Item Master Data (SAP B1)."""

    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, primary_key=True)
    ItemName = models.CharField(ui.ITEM_NAME, max_length=200, db_index=True)
    ItmsGrpCod = models.ForeignKey(
        OITB,
        verbose_name=ui.ITEM_GROUP,
        on_delete=models.PROTECT,
        db_column="ItmsGrpCod",
        related_name="oitm_set",
    )
    InvntItem = models.CharField(ui.INVENTORY_ITEM, max_length=1, default="Y", db_index=True)
    OnHand = models.DecimalField(
        ui.IN_STOCK,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    IsCommited = models.DecimalField(
        ui.COMMITTED,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    OnOrder = models.DecimalField(
        ui.ORDERED,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    ByWh = models.CharField(ui.MANAGE_BY_WAREHOUSE, max_length=1, default="N", db_index=True)
    DfltWH = models.CharField(ui.DEFAULT_WAREHOUSE, max_length=20, blank=True, default="", db_index=True)
    FrgnName = models.CharField(ui.FOREIGN_NAME, max_length=200, blank=True, default="")
    CodeBars = models.CharField(ui.BARCODE, max_length=200, blank=True, default="", db_index=True)
    SalItem = models.CharField(ui.SALES_ITEM, max_length=1, default="Y", db_index=True)
    PrchseItem = models.CharField(ui.PURCHASE_ITEM, max_length=1, default="Y", db_index=True)
    SalUnitMsr = models.CharField(ui.SALES_UOM, max_length=100, blank=True, default="")
    BuyUnitMsr = models.CharField(ui.PURCHASE_UOM, max_length=100, blank=True, default="")
    ValidFor = models.CharField(ui.VALID_FOR, max_length=1, default="Y", db_index=True)
    Frozen = models.CharField(ui.FROZEN, max_length=1, default="N", db_index=True)
    ValidFrom = models.DateField(_("Valid from"), null=True, blank=True, db_index=True)
    ValidTo = models.DateField(_("Valid to"), null=True, blank=True, db_index=True)
    PicturName = models.CharField(ui.ITEM_PICTURE, max_length=200, blank=True, default="")
    SWW = models.CharField(ui.WARRANTY_TEMPLATE, max_length=40, blank=True, default="", db_index=True)
    Weight = models.DecimalField(
        ui.ITEM_WEIGHT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    GrsWeight = models.DecimalField(
        ui.ITEM_GROSS_WEIGHT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Volume = models.DecimalField(
        ui.ITEM_VOLUME,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    VatGourpSa = models.CharField(ui.VAT_GROUP_SALES, max_length=8, blank=True, default="", db_index=True)
    VatGroupPu = models.CharField(ui.VAT_GROUP_PURCHASE, max_length=8, blank=True, default="", db_index=True)
    IUoMEntry = models.IntegerField(ui.UOM_ENTRY_I, null=True, blank=True, db_index=True)
    PUoMEntry = models.IntegerField(ui.UOM_ENTRY_P, null=True, blank=True, db_index=True)

    class Meta:
        db_table = "OITM"
        verbose_name = _("Item master")
        verbose_name_plural = _("Item master data")

    def __str__(self) -> str:
        return f"{self.ItemCode} — {self.ItemName}"

    def clean(self) -> None:
        if self.ItemCode:
            self.ItemCode = self.ItemCode.strip()
        if not self.ItemCode:
            raise ValidationError({"ItemCode": "ItemCode is required."})
        validate_yes_no_char(self.InvntItem)
        validate_yes_no_char(self.ByWh)
        validate_yes_no_char(self.SalItem)
        validate_yes_no_char(self.PrchseItem)
        validate_yes_no_char(self.ValidFor)
        validate_yes_no_char(self.Frozen)
        self.DfltWH = (self.DfltWH or "").strip()[:20]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OITW(models.Model):
    """OITW — Item Warehouse Detail (SAP B1)."""

    pk = models.CompositePrimaryKey("ItemCode", "WhsCode")
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    OnHand = models.DecimalField(
        ui.IN_STOCK,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    IsCommited = models.DecimalField(
        ui.COMMITTED,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    AvgPrice = models.DecimalField(
        ui.AVG_PRICE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    OrderQty = models.DecimalField(
        ui.ORDER_QTY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    MinStock = models.DecimalField(
        ui.MIN_STOCK,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    MaxStock = models.DecimalField(
        ui.MAX_STOCK,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Locked = models.CharField(ui.WAREHOUSE_ROW_LOCKED, max_length=1, default="N", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OITW"
        verbose_name = _("Item warehouse stock")
        verbose_name_plural = _("Item warehouse stock")

    def __str__(self) -> str:
        return f"{self.ItemCode} @ {self.WhsCode}"

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)
        validate_yes_no_char(self.Locked)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OUOM(models.Model):
    """OUOM — UoM Master Data (SAP Business One SDK)."""

    UomEntry = models.BigAutoField(ui.UOM_ENTRY, primary_key=True)
    UomCode = models.CharField(ui.UOM_CODE, max_length=20, unique=True, db_index=True)
    UomName = models.CharField(ui.UOM_NAME, max_length=100, db_index=True)
    Locked = models.CharField(ui.LOCKED, max_length=1, default="N", db_index=True)
    DataSource = models.CharField(ui.DATA_SOURCE, max_length=1, default="N")

    class Meta:
        db_table = "OUOM"
        verbose_name = _("Unit of measure")
        verbose_name_plural = _("Units of measure")

    def __str__(self) -> str:
        return f"{self.UomCode} — {self.UomName}"

    def clean(self) -> None:
        if self.UomCode:
            self.UomCode = self.UomCode.strip()
        if not self.UomCode:
            raise ValidationError({"UomCode": "UomCode is required."})
        if self.Locked not in ("Y", "N"):
            raise ValidationError({"Locked": "Use Y or N."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OWTQ(models.Model):
    """OWTQ — Inventory Transfer Request header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    Handwrtten = models.CharField(ui.HANDWRITTEN, max_length=1, default="N", db_index=True)
    Printed = models.CharField(ui.PRINTED, max_length=1, default="N", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DUE_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, blank=True, default="", db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocRate = models.DecimalField(
        ui.DOC_RATE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
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
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Filler = models.CharField(ui.CREATED_BY, max_length=8, db_index=True)
    Comments = models.CharField(ui.REMARKS, max_length=254, blank=True, default="")
    JrnlMemo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OWTQ"
        verbose_name = _("Inventory transfer request")
        verbose_name_plural = _("Inventory transfer requests")

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)
        _doc_status_oc(self.DocStatus)
        validate_yes_no_char(self.Handwrtten)
        validate_yes_no_char(self.Printed)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WTQ1(models.Model):
    """WTQ1 — Inventory Transfer Request lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OWTQ,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.LINE_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    OpenQty = models.DecimalField(
        ui.OPEN_QUANTITY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
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
    Currency = models.CharField(ui.CURRENCY, max_length=3, blank=True, default="")
    VatGroup = models.CharField(ui.VAT_GROUP_SALES, max_length=8, blank=True, default="")
    FromWhsCod = models.CharField(ui.FROM_WAREHOUSE, max_length=20, db_index=True)
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    LineStatus = models.CharField(ui.LINE_STATUS, max_length=1, default="O", db_index=True)
    TargetType = models.IntegerField(ui.TARGET_TYPE, default=-1)
    TrgetEntry = models.IntegerField(ui.TARGET_ENTRY, null=True, blank=True)
    BaseRef = models.CharField(ui.REFERENCE, max_length=16, blank=True, default="")
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "WTQ1"
        verbose_name = _("Inventory transfer request line")
        verbose_name_plural = _("Inventory transfer request lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="wtq1_itemcode_ix"),
            models.Index(fields=["FromWhsCod"], name="wtq1_fromwhs_ix"),
            models.Index(fields=["WhsCode"], name="wtq1_whscode_ix"),
        ]

    def clean(self) -> None:
        if self.LineStatus not in ("O", "C"):
            raise ValidationError({"LineStatus": "Use O (open) or C (closed)."})
        validate_yes_no_char(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OWTR(models.Model):
    """OWTR — Inventory Transfer header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    Handwrtten = models.CharField(ui.HANDWRITTEN, max_length=1, default="N", db_index=True)
    Printed = models.CharField(ui.PRINTED, max_length=1, default="N", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DUE_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, blank=True, default="", db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocRate = models.DecimalField(
        ui.DOC_RATE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
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
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Filler = models.CharField(ui.CREATED_BY, max_length=20, db_index=True)
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    JrnlMemo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OWTR"
        verbose_name = _("Inventory transfer")
        verbose_name_plural = _("Inventory transfers")

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)
        _doc_status_oc(self.DocStatus)
        validate_yes_no_char(self.Handwrtten)
        validate_yes_no_char(self.Printed)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WTR1(models.Model):
    """WTR1 — Inventory Transfer lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OWTR,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.LINE_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    OpenQty = models.DecimalField(
        ui.OPEN_QUANTITY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    FromWhsCod = models.CharField(ui.FROM_WAREHOUSE, max_length=20, blank=True, default="", db_index=True)
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
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
    Currency = models.CharField(ui.CURRENCY, max_length=3, blank=True, default="")
    VatGroup = models.CharField(ui.VAT_GROUP_SALES, max_length=8, blank=True, default="")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "WTR1"
        verbose_name = _("Inventory transfer line")
        verbose_name_plural = _("Inventory transfer lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="wtr1_itemcode_ix"),
            models.Index(fields=["FromWhsCod"], name="wtr1_fromwhs_ix"),
            models.Index(fields=["WhsCode"], name="wtr1_whscode_ix"),
        ]

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OIGN(models.Model):
    """OIGN — Goods Receipt header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    Handwrtten = models.CharField(ui.HANDWRITTEN, max_length=1, default="N", db_index=True)
    Printed = models.CharField(ui.PRINTED, max_length=1, default="N", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DUE_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, blank=True, default="", db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocRate = models.DecimalField(
        ui.DOC_RATE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
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
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    JrnlMemo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OIGN"
        verbose_name = _("Goods receipt")
        verbose_name_plural = _("Goods receipts")

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)
        _doc_status_oc(self.DocStatus)
        validate_yes_no_char(self.Handwrtten)
        validate_yes_no_char(self.Printed)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class IGN1(models.Model):
    """IGN1 — Goods Receipt lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OIGN,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.LINE_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    OpenQty = models.DecimalField(
        ui.OPEN_QUANTITY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
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
    Currency = models.CharField(ui.CURRENCY, max_length=3, blank=True, default="")
    VatGroup = models.CharField(ui.VAT_GROUP_SALES, max_length=8, blank=True, default="")
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "IGN1"
        verbose_name = _("Goods receipt line")
        verbose_name_plural = _("Goods receipt lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="ign1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="ign1_whscode_ix"),
        ]

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OIGE(models.Model):
    """OIGE — Goods Issue header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    Handwrtten = models.CharField(ui.HANDWRITTEN, max_length=1, default="N", db_index=True)
    Printed = models.CharField(ui.PRINTED, max_length=1, default="N", db_index=True)
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DUE_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, blank=True, default="", db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocRate = models.DecimalField(
        ui.DOC_RATE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
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
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    JrnlMemo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OIGE"
        verbose_name = _("Goods issue")
        verbose_name_plural = _("Goods issues")

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)
        _doc_status_oc(self.DocStatus)
        validate_yes_no_char(self.Handwrtten)
        validate_yes_no_char(self.Printed)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class IGE1(models.Model):
    """IGE1 — Goods Issue lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OIGE,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.LINE_DESCRIPTION, max_length=200, blank=True, default="")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    OpenQty = models.DecimalField(
        ui.OPEN_QUANTITY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    Account = models.CharField(ui.GL_ACCOUNT, max_length=20, blank=True, default="")
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
    Currency = models.CharField(ui.CURRENCY, max_length=3, blank=True, default="")
    VatGroup = models.CharField(ui.VAT_GROUP_SALES, max_length=8, blank=True, default="")
    BaseType = models.IntegerField(ui.BASE_TYPE, null=True, blank=True, db_index=True)
    BaseEntry = models.IntegerField(ui.BASE_ENTRY, null=True, blank=True, db_index=True)
    BaseLine = models.IntegerField(ui.BASE_LINE, null=True, blank=True, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "IGE1"
        verbose_name = _("Goods issue line")
        verbose_name_plural = _("Goods issue lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="ige1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="ige1_whscode_ix"),
        ]

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OINC(models.Model):
    """OINC — Inventory Posting (counting) header (SAP B1)."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    DocStatus = models.CharField(ui.STATUS, max_length=1, default="O", db_index=True)
    Handwrtten = models.CharField(ui.HANDWRITTEN, max_length=1, default="N", db_index=True)
    Printed = models.CharField(ui.PRINTED, max_length=1, default="N", db_index=True)
    CountDate = models.DateField(ui.COUNT_DATE, db_index=True)
    DocDueDate = models.DateField(ui.DUE_DATE, null=True, blank=True, db_index=True)
    TaxDate = models.DateField(ui.DOCUMENT_DATE, null=True, blank=True, db_index=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, blank=True, default="", db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    NumAtCard = models.CharField(ui.BP_REFERENCE_NO, max_length=100, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    DocCur = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    DocRate = models.DecimalField(
        ui.DOC_RATE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DiscSum = models.DecimalField(
        ui.DISCOUNT_TOTAL,
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
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    OwnerCode = models.CharField(ui.OWNER, max_length=50, blank=True, default="", db_index=True)
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    JrnlMemo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OINC"
        verbose_name = _("Inventory posting")
        verbose_name_plural = _("Inventory postings")

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)
        _doc_status_oc(self.DocStatus)
        validate_yes_no_char(self.Handwrtten)
        validate_yes_no_char(self.Printed)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class INC1(models.Model):
    """INC1 — Inventory Posting lines (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OINC,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Dscription = models.CharField(ui.LINE_DESCRIPTION, max_length=200, blank=True, default="")
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    InQty = models.DecimalField(ui.IN_QUANTITY, max_digits=19, decimal_places=6, default=Decimal("0"))
    OutQty = models.DecimalField(ui.OUT_QUANTITY, max_digits=19, decimal_places=6, default=Decimal("0"))
    Difference = models.DecimalField(ui.DIFFERENCE, max_digits=19, decimal_places=6, default=Decimal("0"))
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "INC1"
        verbose_name = _("Inventory posting line")
        verbose_name_plural = _("Inventory posting lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="inc1_itemcode_ix"),
            models.Index(fields=["WhsCode"], name="inc1_whscode_ix"),
        ]

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OINM(models.Model):
    """OINM — Inventory transaction log / stock ledger (SAP B1)."""

    TransNum = models.BigAutoField(ui.TRANSACTION_NO, primary_key=True)
    TransType = models.IntegerField(ui.TRANSACTION_TYPE, db_index=True)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Warehouse = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True)
    InQty = models.DecimalField(ui.IN_QUANTITY, max_digits=19, decimal_places=6, default=Decimal("0"))
    OutQty = models.DecimalField(ui.OUT_QUANTITY, max_digits=19, decimal_places=6, default=Decimal("0"))
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    BASE_REF = models.CharField(ui.USER_REFERENCE, max_length=30, blank=True, default="", db_index=True)
    DocEntry = models.IntegerField(ui.LINKED_DOC_ENTRY, null=True, blank=True, db_index=True)
    DocLineNum = models.IntegerField(ui.LINKED_DOC_LINE, null=True, blank=True)
    TransValue = models.DecimalField(
        ui.TRANSACTION_VALUE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
    )
    CreatedBy = models.CharField(ui.CREATED_BY, max_length=50, blank=True, default="", db_index=True)
    DocTime = models.DateTimeField(ui.POSTING_DATE_TIME, default=timezone.now, db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OINM"
        verbose_name = _("Inventory transaction log")
        verbose_name_plural = _("Inventory transaction log")
        indexes = [
            models.Index(fields=["ItemCode", "Warehouse"], name="oinm_item_wh_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.TransNum} {self.TransType} {self.ItemCode}"

    def clean(self) -> None:
        validate_yes_no_char(self.Canceled)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
