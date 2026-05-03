"""
SAP Business One warehouse master: OWHS (no extra relations beyond B1).
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import b1_ui_labels as ui


class OWHS(models.Model):
    """SAP B1 warehouse master (table ``OWHS``)."""

    WhsCode = models.CharField(ui.WAREHOUSE_CODE, max_length=20, primary_key=True)
    WhsName = models.CharField(ui.WAREHOUSE_NAME, max_length=200, db_index=True)
    Location = models.CharField(ui.LOCATION, max_length=100, blank=True, default="")
    Street = models.CharField(ui.STREET, max_length=100, blank=True, default="")
    StreetNo = models.CharField(ui.STREET_NO, max_length=100, blank=True, default="")
    Building = models.CharField(ui.BUILDING, max_length=100, blank=True, default="")
    Block = models.CharField(ui.BLOCK, max_length=100, blank=True, default="")
    ZipCode = models.CharField(ui.ZIP_CODE, max_length=20, blank=True, default="")
    City = models.CharField(ui.CITY, max_length=100, blank=True, default="", db_index=True)
    County = models.CharField(ui.COUNTY, max_length=100, blank=True, default="")
    State = models.CharField(ui.REGION, max_length=3, blank=True, default="")
    Country = models.CharField(ui.COUNTRY, max_length=3, blank=True, default="", db_index=True)
    Phone1 = models.CharField(ui.PHONE_1, max_length=50, blank=True, default="")
    Phone2 = models.CharField(ui.PHONE_2, max_length=50, blank=True, default="")
    Fax = models.CharField(ui.FAX, max_length=50, blank=True, default="")
    E_Mail = models.CharField(ui.EMAIL, max_length=100, blank=True, default="")
    FederalTaxID = models.CharField(ui.FEDERAL_TAX_ID, max_length=32, blank=True, default="")
    DropShip = models.CharField(ui.DROP_SHIP, max_length=1, default="N", db_index=True)
    BinActivat = models.CharField(ui.BIN_LOCATION_ACTIVE, max_length=1, default="N", db_index=True)
    Locked = models.CharField(ui.WAREHOUSE_MASTER_LOCKED, max_length=1, default="N", db_index=True)
    Inactive = models.CharField(ui.INACTIVE, max_length=1, default="N", db_index=True)

    class Meta:
        db_table = "OWHS"
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")
        indexes = [
            models.Index(fields=["WhsCode"], name="owhs_whscode_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.WhsCode} — {self.WhsName}"

    def clean(self) -> None:
        if self.WhsCode:
            self.WhsCode = self.WhsCode.strip()
        if not self.WhsCode:
            raise ValidationError({"WhsCode": "WhsCode is required."})
        if self.Inactive not in ("Y", "N"):
            raise ValidationError({"Inactive": "Use Y or N."})
        for fld in ("DropShip", "BinActivat", "Locked"):
            v = getattr(self, fld)
            if v not in ("Y", "N"):
                raise ValidationError({fld: "Use Y or N."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
