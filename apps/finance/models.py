"""
SAP Business One–style Finance: chart of accounts (OACT), profit/cost centers (OPRC),
journal entries (OJDT/JDT1), incoming/outgoing payments (ORCT/RCT1, OVPM/VPM1),
tax codes (OSTC), financial periods (OFPR), budget (OBGT/BGT1).

Headers use ``BigAutoField`` where SAP uses sequential keys; master tables use natural keys.
Lines use ``CompositePrimaryKey`` where applicable.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import b1_ui_labels as ui
from apps.core.beginner_style.model_validation import (
    validate_dimension_1_to_5,
    validate_finance_document_status_open_or_closed,
    validate_gl_group_mask_1_to_5,
    validate_yes_no_field,
)


class OACT(models.Model):
    """OACT — Chart of accounts."""

    AcctCode = models.CharField(ui.ACCOUNT_CODE, primary_key=True, max_length=20, db_index=True)
    AcctName = models.CharField(ui.ACCOUNT_NAME, max_length=200)
    CurrTotal = models.DecimalField(
        ui.BALANCE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    GroupMask = models.PositiveSmallIntegerField(ui.ACCOUNT_TYPE, db_index=True)
    FatherNum = models.CharField(ui.FATHER_ACCOUNT, max_length=20, blank=True, default="", db_index=True)
    Postable = models.CharField(ui.POSTING_ALLOWED, max_length=1, default="Y", db_index=True)
    LocCash = models.CharField(ui.CASH_ACCOUNT_FLAG, max_length=1, default="N", db_index=True)
    ValidFor = models.CharField(ui.VALID_FOR, max_length=1, default="Y", db_index=True)
    Frozen = models.CharField(ui.FROZEN, max_length=1, default="N", db_index=True)
    Levels = models.PositiveSmallIntegerField(ui.GL_LEVELS, default=1)
    ExportCode = models.CharField(ui.EXPORT_CODE, max_length=20, blank=True, default="", db_index=True)
    AcctFixed = models.CharField(ui.FIXED_ASSET_ACCOUNT, max_length=1, default="N", db_index=True)
    U_UserFld1 = models.CharField(ui.USER_FIELD_1, max_length=254, blank=True, default="", db_column="U_UserFld1")
    U_UserFld2 = models.CharField(ui.USER_FIELD_2, max_length=254, blank=True, default="", db_column="U_UserFld2")

    class Meta:
        db_table = "OACT"
        verbose_name = _("G/L account")
        verbose_name_plural = _("Chart of accounts")

    def clean(self) -> None:
        validate_gl_group_mask_1_to_5(int(self.GroupMask))
        validate_yes_no_field(self.Postable, "Postable")
        validate_yes_no_field(self.LocCash, "LocCash")
        validate_yes_no_field(self.ValidFor, "ValidFor")
        validate_yes_no_field(self.Frozen, "Frozen")
        validate_yes_no_field(self.AcctFixed, "AcctFixed")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OPRC(models.Model):
    """OPRC — Cost / profit center."""

    PrcCode = models.CharField(ui.PROFIT_CENTER, primary_key=True, max_length=20, db_index=True)
    PrcName = models.CharField(ui.PROFIT_CENTER_NAME, max_length=200)
    DimCode = models.PositiveSmallIntegerField(ui.DIMENSION_NO)
    Active = models.CharField(ui.ACTIVE, max_length=1, default="Y", db_index=True)
    PrcFather = models.CharField(ui.CENTER_PARENT, max_length=20, blank=True, default="", db_index=True)
    U_UserFld1 = models.CharField(ui.USER_FIELD_1, max_length=254, blank=True, default="", db_column="U_UserFld1")
    U_UserFld2 = models.CharField(ui.USER_FIELD_2, max_length=254, blank=True, default="", db_column="U_UserFld2")

    class Meta:
        db_table = "OPRC"
        verbose_name = _("Profit / cost center")
        verbose_name_plural = _("Profit / cost centers")

    def clean(self) -> None:
        validate_dimension_1_to_5(int(self.DimCode))
        validate_yes_no_field(self.Active, "Active")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OJDT(models.Model):
    """OJDT — Journal entry header."""

    TransId = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    BaseRef = models.CharField(ui.REFERENCE, max_length=200, blank=True, default="", db_index=True)
    RefDate = models.DateField(ui.POSTING_DATE, db_index=True)
    TransType = models.IntegerField(ui.TRANSACTION_TYPE, db_index=True)
    Memo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    Ref1 = models.CharField(ui.JOURNAL_REF_1, max_length=100, blank=True, default="", db_index=True)
    Ref2 = models.CharField(ui.JOURNAL_REF_2, max_length=100, blank=True, default="", db_index=True)
    DueDate = models.DateField(ui.JOURNAL_DUE_DATE, null=True, blank=True, db_index=True)
    TransCode = models.IntegerField(ui.TRANS_CODE, null=True, blank=True, db_index=True)
    Project = models.CharField(ui.PROJECT_CODE, max_length=20, blank=True, default="", db_index=True)
    U_UserFld1 = models.CharField(ui.USER_FIELD_1, max_length=254, blank=True, default="", db_column="U_UserFld1")
    U_UserFld2 = models.CharField(ui.USER_FIELD_2, max_length=254, blank=True, default="", db_column="U_UserFld2")

    class Meta:
        db_table = "OJDT"
        verbose_name = _("Journal entry")
        verbose_name_plural = _("Journal entries")


class JDT1(models.Model):
    """JDT1 — Journal entry lines."""

    pk = models.CompositePrimaryKey("header", "Line_ID")
    header = models.ForeignKey(
        OJDT,
        verbose_name=_("Journal entry"),
        on_delete=models.CASCADE,
        db_column="TransId",
        related_name="lines",
    )
    Line_ID = models.IntegerField(ui.JOURNAL_LINE_ID, db_column="Line_ID")
    Account = models.CharField(ui.GL_ACCOUNT, max_length=20, db_index=True)
    ShortName = models.CharField(ui.SHORT_NAME, max_length=50, blank=True, default="", db_index=True)
    Debit = models.DecimalField(
        ui.DEBIT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Credit = models.DecimalField(
        ui.CREDIT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    ProfitCode = models.CharField(ui.PROFIT_CENTER_CODE, max_length=20, blank=True, default="", db_index=True)
    LineMemo = models.TextField(ui.LINE_MEMO, blank=True, default="")
    Ref1 = models.CharField(ui.JOURNAL_REF_1, max_length=100, blank=True, default="", db_index=True)
    Ref2 = models.CharField(ui.JOURNAL_REF_2, max_length=100, blank=True, default="", db_index=True)
    Ref3Line = models.CharField(ui.LINE_REF_3, max_length=100, blank=True, default="", db_index=True)
    DueDate = models.DateField(ui.LINE_DUE_DATE, null=True, blank=True, db_index=True)
    VatGroup = models.CharField(ui.VAT_GROUP_SALES, max_length=8, blank=True, default="", db_index=True)
    OcrCode = models.CharField(ui.OCR_CODE, max_length=11, blank=True, default="", db_index=True)

    class Meta:
        db_table = "JDT1"
        verbose_name = _("Journal entry line")
        verbose_name_plural = _("Journal entry lines")


class ORCT(models.Model):
    """ORCT — Incoming payment header."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    CashAcct = models.CharField(ui.CASH_ACCOUNT, max_length=20, blank=True, default="")
    CheckAcct = models.CharField(ui.CHECK_ACCOUNT, max_length=20, blank=True, default="")
    DocTotal = models.DecimalField(
        ui.DOCUMENT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    CashSum = models.DecimalField(
        ui.CASH_AMOUNT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DocStatus = models.CharField(ui.PAYMENT_DOC_STATUS, max_length=1, default="O", db_index=True)
    TrsfrAcct = models.CharField(ui.TRANSFER_ACCOUNT, max_length=20, blank=True, default="", db_index=True)
    CheckSum = models.DecimalField(
        ui.CHECK_SUM,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    JrnlMemo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    U_UserFld1 = models.CharField(ui.USER_FIELD_1, max_length=254, blank=True, default="", db_column="U_UserFld1")
    U_UserFld2 = models.CharField(ui.USER_FIELD_2, max_length=254, blank=True, default="", db_column="U_UserFld2")

    class Meta:
        db_table = "ORCT"
        verbose_name = _("Incoming payment")
        verbose_name_plural = _("Incoming payments")

    def clean(self) -> None:
        validate_finance_document_status_open_or_closed(self.DocStatus)


class RCT1(models.Model):
    """RCT1 — Incoming payment lines (applied amounts)."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        ORCT,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    SumApplied = models.DecimalField(
        ui.APPLIED_AMOUNT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    InvType = models.IntegerField(ui.INVOICE_TYPE, default=0, db_index=True)

    class Meta:
        db_table = "RCT1"
        verbose_name = _("Incoming payment line")
        verbose_name_plural = _("Incoming payment lines")


class OVPM(models.Model):
    """OVPM — Outgoing payment header."""

    DocEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    CardCode = models.CharField(ui.BP_CODE, max_length=15, db_index=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, blank=True, default="")
    DocDate = models.DateField(ui.POSTING_DATE, db_index=True)
    BankAcct = models.CharField(ui.BANK_ACCOUNT, max_length=20, blank=True, default="")
    CashSum = models.DecimalField(
        ui.CASH_AMOUNT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    TrsfrSum = models.DecimalField(
        ui.BANK_TRANSFER,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DocTotal = models.DecimalField(
        ui.DOCUMENT_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DocStatus = models.CharField(ui.PAYMENT_DOC_STATUS, max_length=1, default="O", db_index=True)
    TrsfrAcct = models.CharField(ui.TRANSFER_ACCOUNT, max_length=20, blank=True, default="", db_index=True)
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    JrnlMemo = models.TextField(ui.JOURNAL_MEMO, blank=True, default="")
    U_UserFld1 = models.CharField(ui.USER_FIELD_1, max_length=254, blank=True, default="", db_column="U_UserFld1")
    U_UserFld2 = models.CharField(ui.USER_FIELD_2, max_length=254, blank=True, default="", db_column="U_UserFld2")

    class Meta:
        db_table = "OVPM"
        verbose_name = _("Outgoing payment")
        verbose_name_plural = _("Outgoing payments")

    def clean(self) -> None:
        validate_finance_document_status_open_or_closed(self.DocStatus)


class VPM1(models.Model):
    """VPM1 — Outgoing payment lines."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OVPM,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="DocEntry",
        related_name="lines",
    )
    LineNum = models.IntegerField(ui.LINE_NO)
    DocNum = models.IntegerField(ui.DOCUMENT_NO, null=True, blank=True, db_index=True)
    SumApplied = models.DecimalField(
        ui.APPLIED_AMOUNT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    InvType = models.IntegerField(ui.INVOICE_TYPE, default=0, db_index=True)

    class Meta:
        db_table = "VPM1"
        verbose_name = _("Outgoing payment line")
        verbose_name_plural = _("Outgoing payment lines")


class OSTC(models.Model):
    """OSTC — Tax code."""

    Code = models.CharField(ui.CODE, primary_key=True, max_length=20, db_index=True)
    Name = models.CharField(ui.NAME, max_length=200)
    Rate = models.DecimalField(
        ui.RATE,
        max_digits=9,
        decimal_places=4,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    Account = models.CharField(ui.TAX_ACCOUNT, max_length=20, blank=True, default="", db_index=True)
    ValidFor = models.CharField(ui.VALID_FOR, max_length=1, default="Y", db_index=True)
    Frozen = models.CharField(ui.FROZEN, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OSTC"
        verbose_name = _("Tax code")
        verbose_name_plural = _("Tax codes")

    def clean(self) -> None:
        validate_yes_no_field(self.ValidFor, "ValidFor")
        validate_yes_no_field(self.Frozen, "Frozen")


class OFPR(models.Model):
    """OFPR — Financial period."""

    AbsEntry = models.BigAutoField(ui.INTERNAL_NO, primary_key=True)
    PeriodCode = models.CharField(ui.SUBPERIOD_CODE, max_length=20, unique=True, db_index=True)
    F_RefDate = models.DateField(ui.PERIOD_FROM)
    T_RefDate = models.DateField(ui.PERIOD_TO)
    PeriodStat = models.CharField(ui.PERIOD_STATUS, max_length=20, default="Unlocked", db_index=True)

    class Meta:
        db_table = "OFPR"
        verbose_name = _("Financial period")
        verbose_name_plural = _("Financial periods")

    def clean(self) -> None:
        if self.F_RefDate and self.T_RefDate and self.F_RefDate > self.T_RefDate:
            raise ValidationError({"T_RefDate": "End date must be on or after start date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OBGT(models.Model):
    """OBGT — Budget per GL account."""

    AcctCode = models.OneToOneField(
        OACT,
        verbose_name=ui.ACCOUNT_CODE,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="AcctCode",
        related_name="budget",
    )
    BudgTotal = models.DecimalField(
        ui.BUDGET_TOTAL,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        db_table = "OBGT"
        verbose_name = _("Budget setup")
        verbose_name_plural = _("Budget setups")


class BGT1(models.Model):
    """BGT1 — Budget lines by month and cost center."""

    pk = models.CompositePrimaryKey("header", "Month", "PrcCode")
    header = models.ForeignKey(
        OBGT,
        verbose_name=ui.ACCOUNT_CODE,
        on_delete=models.CASCADE,
        db_column="AcctCode",
        related_name="lines",
    )
    Month = models.PositiveSmallIntegerField(
        ui.MONTH, validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    PrcCode = models.CharField(ui.PROFIT_CENTER, max_length=20, blank=True, default="", db_index=True)
    PlannedAmt = models.DecimalField(
        ui.PLANNED_AMOUNT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        db_table = "BGT1"
        verbose_name = _("Budget line")
        verbose_name_plural = _("Budget lines")


# --- SAP B1–named stubs (master / banking / fixed assets) — extend fields & Bolt API as needed ---


class OACD(models.Model):
    """OACD — Asset class (fixed assets)."""

    AbsId = models.AutoField(primary_key=True)
    Name = models.CharField(_("Name"), max_length=200, blank=True, default="")

    class Meta:
        db_table = "OACD"
        verbose_name = _("Asset class")
        verbose_name_plural = _("Asset classes (OACD)")


class OADM(models.Model):
    """OADM — Administration / company financial setup (single logical row per tenant)."""

    AbsEntry = models.AutoField(primary_key=True)
    MainCurncy = models.CharField(_("Main currency"), max_length=3, blank=True, default="")
    CompnyName = models.CharField(_("Company name"), max_length=200, blank=True, default="")

    class Meta:
        db_table = "OADM"
        verbose_name = _("Administration setup")
        verbose_name_plural = _("Administration setup (OADM)")


class OAGS(models.Model):
    """OAGS — Asset group."""

    GroupCode = models.AutoField(primary_key=True)
    GroupName = models.CharField(_("Group name"), max_length=200, blank=True, default="")

    class Meta:
        db_table = "OAGS"
        verbose_name = _("Asset group")
        verbose_name_plural = _("Asset groups (OAGS)")


class OCTD(models.Model):
    """OCTD — Credit card type / card definition."""

    CreditCard = models.CharField(_("Credit card"), max_length=40, primary_key=True)
    CardName = models.CharField(_("Card name"), max_length=200, blank=True, default="")

    class Meta:
        db_table = "OCTD"
        verbose_name = _("Credit card")
        verbose_name_plural = _("Credit cards (OCTD)")


class OVTG(models.Model):
    """OVTG — VAT / tax group (distinct from OSTC tax codes in this schema)."""

    Code = models.CharField(_("Code"), max_length=20, primary_key=True)
    Name = models.CharField(_("Name"), max_length=200, blank=True, default="")
    Rate = models.DecimalField(
        _("Rate"),
        max_digits=9,
        decimal_places=4,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )

    class Meta:
        db_table = "OVTG"
        verbose_name = _("VAT group")
        verbose_name_plural = _("VAT groups (OVTG)")


class OFAV(models.Model):
    """OFAV — Asset values (snapshot)."""

    AbsEntry = models.AutoField(primary_key=True)
    AssetCode = models.CharField(_("Asset code"), max_length=20, blank=True, default="", db_index=True)
    CardCode = models.CharField(_("BP code"), max_length=15, blank=True, default="", db_index=True)

    class Meta:
        db_table = "OFAV"
        verbose_name = _("Asset value")
        verbose_name_plural = _("Asset values (OFAV)")


class OAFR(models.Model):
    """OAFR — Asset revaluation header."""

    AbsEntry = models.AutoField(primary_key=True)
    AssetCode = models.CharField(_("Asset code"), max_length=20, blank=True, default="", db_index=True)
    PostDate = models.DateField(_("Posting date"), null=True, blank=True)

    class Meta:
        db_table = "OAFR"
        verbose_name = _("Asset revaluation")
        verbose_name_plural = _("Asset revaluations (OAFR)")


class AAC1(models.Model):
    """AAC1 — Asset class × depreciation area."""

    Id = models.AutoField(primary_key=True)
    ClassId = models.PositiveIntegerField(_("Asset class id"), db_index=True)
    AreaId = models.CharField(_("Area id"), max_length=10, blank=True, default="", db_index=True)

    class Meta:
        db_table = "AAC1"
        verbose_name = _("Asset class depreciation area")
        verbose_name_plural = _("Asset class depreciation areas (AAC1)")


class ODRN(models.Model):
    """ODRN — Depreciation run."""

    DocEntry = models.AutoField(primary_key=True)
    F_RefDate = models.DateField(_("From date"), null=True, blank=True)
    T_RefDate = models.DateField(_("To date"), null=True, blank=True)
    Memo = models.CharField(_("Memo"), max_length=200, blank=True, default="")

    class Meta:
        db_table = "ODRN"
        verbose_name = _("Depreciation run")
        verbose_name_plural = _("Depreciation runs (ODRN)")


class OITL(models.Model):
    """OITL — Internal reconciliation header."""

    ReconNum = models.BigAutoField(primary_key=True)
    CardCode = models.CharField(_("BP code"), max_length=15, blank=True, default="", db_index=True)
    ReconDate = models.DateField(_("Recon date"), null=True, blank=True)

    class Meta:
        db_table = "OITL"
        verbose_name = _("Internal reconciliation")
        verbose_name_plural = _("Internal reconciliations (OITL)")


class ITL1(models.Model):
    """ITL1 — Internal reconciliation rows."""

    pk = models.CompositePrimaryKey("header", "LineNum")
    header = models.ForeignKey(
        OITL,
        verbose_name=_("Reconciliation"),
        on_delete=models.CASCADE,
        db_column="ReconNum",
        related_name="lines",
    )
    LineNum = models.IntegerField(_("Line no."))
    ShortName = models.CharField(_("Short name"), max_length=50, blank=True, default="")
    Debit = models.DecimalField(
        _("Debit"),
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Credit = models.DecimalField(
        _("Credit"),
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        db_table = "ITL1"
        verbose_name = _("Internal reconciliation line")
        verbose_name_plural = _("Internal reconciliation lines (ITL1)")


class OIBT(models.Model):
    """OIBT — Bank transfer / interbank movement header."""

    DocEntry = models.BigAutoField(primary_key=True)
    TrnsfrDate = models.DateField(_("Transfer date"), null=True, blank=True)
    TrnsfrSum = models.DecimalField(
        _("Amount"),
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Memo = models.CharField(_("Memo"), max_length=200, blank=True, default="")

    class Meta:
        db_table = "OIBT"
        verbose_name = _("Bank transfer")
        verbose_name_plural = _("Bank transfers (OIBT)")
