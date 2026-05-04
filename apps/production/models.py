"""
SAP Business One Production: BOM (OITT/ITT1), production order (OWOR/WOR1).

Issue/receipt documents use the same SAP tables as inventory — call
``/api/inventory/oige``, ``/api/inventory/ige1``, ``/api/inventory/oign``,
``/api/inventory/ign1`` with ``BaseType=202`` and ``BaseEntry`` = ``OWOR.DocEntry``.

``Canceled`` = Y/N soft delete (same pattern as ``apps.sales`` / ``apps.purchase``).
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import b1_ui_labels as ui
from apps.core.beginner_style.model_validation import (
    validate_bom_line_issue_method_manual_backflush_or_mixed,
    validate_production_bom_tree_type,
    validate_production_order_status_planned_released_or_closed,
    validate_yes_no_field,
)


class OITT(models.Model):
    """OITT — Bill of Materials header (parent finished item)."""

    Code = models.CharField(ui.PRODUCT_NO, max_length=50, primary_key=True)
    TreeType = models.CharField(ui.BOM_CATEGORY, max_length=1, default="P", db_index=True)
    Quantity = models.DecimalField(
        ui.BASE_QUANTITY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("1"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Base quantity (e.g. per 1 finished unit).",
    )
    TreeName = models.CharField(ui.BOM_DISPLAY_NAME, max_length=200, blank=True, default="", db_index=True)
    Locked = models.CharField(ui.BOM_HEADER_LOCKED, max_length=1, default="N", db_index=True)
    U_UserFld1 = models.CharField(ui.USER_FIELD_1, max_length=254, blank=True, default="", db_column="U_UserFld1")
    U_UserFld2 = models.CharField(ui.USER_FIELD_2, max_length=254, blank=True, default="", db_column="U_UserFld2")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OITT"
        verbose_name = _("Bill of materials")
        verbose_name_plural = _("Bills of materials")

    def clean(self) -> None:
        validate_production_bom_tree_type(self.TreeType)
        validate_yes_no_field(self.Canceled, "Canceled")
        validate_yes_no_field(self.Locked, "Locked")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ITT1(models.Model):
    """ITT1 — BOM lines (components / raw materials)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OITT,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="Father",
        to_field="Code",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True, db_column="Code")
    Quantity = models.DecimalField(ui.QUANTITY, max_digits=19, decimal_places=6)
    Price = models.DecimalField(ui.UNIT_PRICE, max_digits=19, decimal_places=6, default=Decimal("0"))
    Currency = models.CharField(ui.CURRENCY, max_length=3, blank=True, default="")
    IssueMeth = models.CharField(ui.ISSUE_METHOD, max_length=1, default="M", db_index=True)
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True, db_column="Warehouse")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "ITT1"
        verbose_name = _("BOM line")
        verbose_name_plural = _("BOM lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="itt1_item_ix"),
        ]

    def clean(self) -> None:
        validate_yes_no_field(self.Canceled, "Canceled")
        validate_bom_line_issue_method_manual_backflush_or_mixed(self.IssueMeth)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OWOR(models.Model):
    """OWOR — Production order header."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    Status = models.CharField(ui.PRODUCTION_STATUS, max_length=1, default="P", db_index=True)
    PlannedQty = models.DecimalField(ui.PLANNED_QTY, max_digits=19, decimal_places=6)
    CmpltQty = models.DecimalField(
        ui.COMPLETED_QTY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    PostDate = models.DateField(ui.POSTING_DATE, db_index=True)
    DueDate = models.DateField(ui.PRODUCTION_DUE_DATE, null=True, blank=True, db_index=True)
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True, db_column="Warehouse")
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    Project = models.CharField(ui.PROJECT_CODE, max_length=20, blank=True, default="", db_index=True)
    OrigType = models.IntegerField(ui.ORIGIN_TYPE, null=True, blank=True, db_index=True)
    OrigEntry = models.IntegerField(ui.ORIGIN_ENTRY, null=True, blank=True, db_index=True)
    U_UserFld1 = models.CharField(ui.USER_FIELD_1, max_length=254, blank=True, default="", db_column="U_UserFld1")
    U_UserFld2 = models.CharField(ui.USER_FIELD_2, max_length=254, blank=True, default="", db_column="U_UserFld2")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OWOR"
        verbose_name = _("Production order")
        verbose_name_plural = _("Production orders")

    def clean(self) -> None:
        validate_production_order_status_planned_released_or_closed(self.Status)
        validate_yes_no_field(self.Canceled, "Canceled")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WOR1(models.Model):
    """WOR1 — Production order component lines."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OWOR,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    ItemCode = models.CharField(ui.ITEM_CODE, max_length=50, db_index=True)
    PlannedQty = models.DecimalField(ui.PLANNED_QTY, max_digits=19, decimal_places=6)
    IssuedQty = models.DecimalField(
        ui.ISSUED_QTY,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    VisOrder = models.IntegerField(ui.VISUAL_ORDER, default=0, db_index=True)
    LineText = models.TextField(ui.LINE_TEXT, blank=True, default="")
    WhsCode = models.CharField(ui.WAREHOUSE, max_length=20, db_index=True, db_column="wareHouse")
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "WOR1"
        verbose_name = _("Production order line")
        verbose_name_plural = _("Production order lines")
        indexes = [
            models.Index(fields=["ItemCode"], name="wor1_item_ix"),
        ]

    def clean(self) -> None:
        validate_yes_no_field(self.Canceled, "Canceled")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
