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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
