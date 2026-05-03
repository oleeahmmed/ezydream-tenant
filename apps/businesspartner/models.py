"""
SAP Business One–style business partners: ``OCRG`` (BP groups), ``OCRD`` (master),
``CRD1`` (addresses: Bill-to / Ship-to and more).
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import b1_ui_labels as ui


def _yn(value: str, field: str) -> None:
    if value not in ("Y", "N"):
        raise ValidationError({field: "Use Y or N."})


class OCRG(models.Model):
    """OCRG — Business Partner Group (SAP B1)."""

    GroupCode = models.PositiveSmallIntegerField(ui.BP_GROUP, primary_key=True)
    GroupName = models.CharField(ui.BP_GROUP_NAME, max_length=100, db_index=True)
    GroupType = models.CharField(ui.GROUP_TYPE, max_length=1, default="B", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OCRG"
        verbose_name = _("BP group")
        verbose_name_plural = _("BP groups")

    def __str__(self) -> str:
        return f"{self.GroupCode} — {self.GroupName}"

    def clean(self) -> None:
        if self.GroupType not in ("C", "S", "B"):
            raise ValidationError({"GroupType": "Use C (customer), S (supplier), or B (both)."})
        _yn(self.Canceled, "Canceled")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OCRD(models.Model):
    """OCRD — Business Partner master (SAP B1)."""

    CardCode = models.CharField(ui.BP_CODE, max_length=15, primary_key=True)
    CardName = models.CharField(ui.BP_NAME, max_length=200, db_index=True)
    CardType = models.CharField(ui.BP_TYPE, max_length=1, default="C", db_index=True)
    GroupCode = models.ForeignKey(
        OCRG,
        verbose_name=ui.BP_GROUP,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="GroupCode",
        related_name="partners",
    )
    CardFName = models.CharField(ui.FOREIGN_NAME, max_length=200, blank=True, default="")
    CntctPrsn = models.CharField(ui.CONTACT_PERSON, max_length=100, blank=True, default="", db_index=True)
    Phone1 = models.CharField(ui.PHONE_1, max_length=50, blank=True, default="")
    Phone2 = models.CharField(ui.PHONE_2, max_length=50, blank=True, default="")
    Fax = models.CharField(ui.FAX, max_length=50, blank=True, default="")
    Cellular = models.CharField(ui.CELLULAR, max_length=50, blank=True, default="")
    E_Mail = models.CharField(ui.EMAIL, max_length=100, blank=True, default="", db_index=True)
    Website = models.CharField(ui.WEBSITE, max_length=100, blank=True, default="")
    LicTradNum = models.CharField(ui.TAX_ID, max_length=32, blank=True, default="", db_index=True)
    CreditLine = models.DecimalField(
        ui.CREDIT_LIMIT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DebtLine = models.DecimalField(
        ui.DEBT_LIMIT,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Balance = models.DecimalField(
        ui.CURRENT_BALANCE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
    )
    OrdersBal = models.DecimalField(
        ui.OPEN_ORDERS_BALANCE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    DNotesBal = models.DecimalField(
        ui.OPEN_DELIVERIES_BALANCE,
        max_digits=19,
        decimal_places=6,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    Currency = models.CharField(ui.CURRENCY, max_length=15, blank=True, default="", db_index=True)
    PayTermsGrpCode = models.IntegerField(ui.PAYMENT_TERMS_GROUP, null=True, blank=True, db_index=True)
    DfltWhs = models.CharField(ui.DEFAULT_WAREHOUSE, max_length=20, blank=True, default="", db_index=True)
    ShipToDef = models.CharField(ui.SHIP_TO_DEFAULT, max_length=50, blank=True, default="")
    BillToDef = models.CharField(ui.BILL_TO_DEFAULT, max_length=50, blank=True, default="")
    SlpCode = models.IntegerField(ui.SALES_EMPLOYEE, null=True, blank=True, db_index=True)
    Comments = models.TextField(ui.REMARKS, blank=True, default="")
    ValidFor = models.CharField(ui.VALID_FOR, max_length=1, default="Y", db_index=True)
    Frozen = models.CharField(ui.FROZEN, max_length=1, default="N", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OCRD"
        verbose_name = _("Business partner")
        verbose_name_plural = _("Business partners")
        indexes = [
            models.Index(fields=["CardName"], name="ocrd_cardname_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.CardCode} — {self.CardName}"

    def clean(self) -> None:
        if self.CardCode:
            self.CardCode = self.CardCode.strip()
        if not self.CardCode:
            raise ValidationError({"CardCode": "CardCode is required."})
        if self.CardType not in ("C", "S", "L"):
            raise ValidationError({"CardType": "Use C (customer), S (supplier), or L (lead)."})
        _yn(self.ValidFor, "ValidFor")
        _yn(self.Frozen, "Frozen")
        _yn(self.Canceled, "Canceled")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class CRD1(models.Model):
    """CRD1 — Business Partner address rows (SAP B1)."""

    pk = models.CompositePrimaryKey("header", "Address")
    header = models.ForeignKey(
        OCRD,
        verbose_name=ui.PARENT_DOCUMENT,
        on_delete=models.CASCADE,
        db_column="CardCode",
        related_name="addresses",
    )
    Address = models.CharField(ui.ADDRESS_ID, max_length=50, db_index=True)
    Street = models.CharField(ui.STREET, max_length=100, blank=True, default="")
    Block = models.CharField(ui.BLOCK, max_length=100, blank=True, default="")
    City = models.CharField(ui.CITY, max_length=100, blank=True, default="", db_index=True)
    County = models.CharField(ui.COUNTY, max_length=100, blank=True, default="")
    ZipCode = models.CharField(ui.ZIP_CODE, max_length=20, blank=True, default="")
    Country = models.CharField(ui.COUNTRY, max_length=3, blank=True, default="", db_index=True)
    State = models.CharField(ui.REGION, max_length=3, blank=True, default="")
    Building = models.CharField(ui.BUILDING, max_length=100, blank=True, default="")
    AdresType = models.CharField(ui.ADDRESS_TYPE, max_length=1, default="S", db_index=True)
    Canceled = models.CharField(ui.CANCELED, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "CRD1"
        verbose_name = _("BP address")
        verbose_name_plural = _("BP addresses")
        indexes = [
            models.Index(fields=["City"], name="crd1_city_ix"),
        ]

    def clean(self) -> None:
        if self.AdresType not in ("B", "S"):
            raise ValidationError({"AdresType": "Use B (bill-to) or S (ship-to)."})
        _yn(self.Canceled, "Canceled")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
