"""
ERP / POS / inventory foundation (per django-tenants **schema** — no row-level ``Tenant`` FK).
"""

from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Warehouse(models.Model):
    """Storage / fulfillment location."""

    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_wh_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_wh_is_cd_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def clean(self) -> None:
        if self.code:
            self.code = self.code.strip()
        if not self.code:
            raise ValidationError({"code": "Code is required."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Category(models.Model):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_cat_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_cat_is_cd_ix"),
        ]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class UnitOfMeasure(models.Model):
    code = models.CharField(max_length=20, db_index=True)
    name = models.CharField(max_length=100, db_index=True)
    decimal_places = models.PositiveSmallIntegerField(
        default=0,
        help_text="Decimal places allowed for quantities in this UOM.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_uom_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_uom_is_cd_ix"),
        ]
        verbose_name = "Unit of measure"
        verbose_name_plural = "Units of measure"

    def __str__(self) -> str:
        return f"{self.code} ({self.name})"


class Currency(models.Model):
    code = models.CharField(max_length=10, db_index=True, help_text="e.g. USD, BDT")
    name = models.CharField(max_length=100, db_index=True)
    symbol = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_curr_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_curr_is_cd_ix"),
        ]
        verbose_name_plural = "currencies"

    def __str__(self) -> str:
        return f"{self.code} ({self.name})"


class TaxType(models.Model):
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_taxtype_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_taxtype_is_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class TaxRate(models.Model):
    """Percentage for a tax type (time-bounded)."""

    tax_type = models.ForeignKey(
        TaxType,
        on_delete=models.CASCADE,
        related_name="rates",
    )
    rate_percent = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Percent, e.g. 15.0000 for 15%.",
    )
    effective_from = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_from", "tax_type__code"]
        indexes = [
            models.Index(fields=("tax_type", "effective_from"), name="f1_taxrate_ty_dt_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.tax_type.code} {self.rate_percent}% from {self.effective_from}"


class Customer(models.Model):
    code = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Sold-to party number — unique (SAP-style customer account).",
    )
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_cust_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_cust_is_cd_ix"),
        ]
        verbose_name_plural = "customers"

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def clean(self) -> None:
        if self.code:
            self.code = self.code.strip()
        if not self.code:
            raise ValidationError({"code": "Code is required."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class Supplier(models.Model):
    code = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Vendor account — unique (SAP-style supplier number).",
    )
    name = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="suppliers",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_sup_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_sup_is_cd_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def clean(self) -> None:
        if self.code:
            self.code = self.code.strip()
        if not self.code:
            raise ValidationError({"code": "Code is required."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class SalesPerson(models.Model):
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_sp_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_sp_is_cd_ix"),
        ]
        verbose_name_plural = "sales persons"

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class PaymentMethod(models.Model):
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_paym_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_paym_is_cd_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class PaymentTerm(models.Model):
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    days_until_due = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Days after invoice date (empty for immediate / COD).",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_payt_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_payt_is_cd_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class Product(models.Model):
    """Sellable / stockable item."""

    code = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Material / product number — unique (SAP-style MATNR).",
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    default_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products_default_uom",
    )
    default_warehouse = models.ForeignKey(
        Warehouse,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products_default_warehouse",
        help_text="Primary fulfillment / default stock view for this material.",
    )
    default_unit_cost = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    list_price = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_prod_code_uq"),
        ]
        indexes = [
            models.Index(fields=("is_active", "code"), name="f1_prod_is_cd_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"

    def clean(self) -> None:
        if self.code:
            self.code = self.code.strip()
        if not self.code:
            raise ValidationError({"code": "Code is required."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    code = models.CharField(max_length=100, db_index=True)
    name = models.CharField(
        max_length=255,
        help_text="Short description (SAP-style variant text).",
    )
    barcode = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product", "code"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_pvar_code_uq"),
        ]
        indexes = [
            models.Index(fields=("product", "is_active"), name="f1_pvar_prod_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.product.code} / {self.code} — {self.name}"

    def clean(self) -> None:
        if self.code:
            self.code = self.code.strip()
        if not self.code:
            raise ValidationError({"code": "Code is required."})
        if self.name:
            self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "Name is required."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ProductBom(models.Model):
    """SAP-style BOM header (material + optional plant + usage + alternative + validity)."""

    class Usage(models.TextChoices):
        PRODUCTION = "1", "Production"
        COSTING = "2", "Costing"
        ENGINEERING = "3", "Engineering"

    code = models.CharField(
        max_length=50,
        db_index=True,
        help_text="BOM number / document id (unique in schema).",
    )
    name = models.CharField(max_length=200, db_index=True)
    parent_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="boms",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="boms",
        help_text="Optional plant (Werks). Empty = not restricted to one warehouse.",
    )
    usage = models.CharField(
        max_length=1,
        choices=Usage.choices,
        default=Usage.PRODUCTION,
        db_index=True,
    )
    alternative = models.PositiveSmallIntegerField(
        default=1,
        help_text="Alternative BOM (STALT).",
    )
    valid_from = models.DateField(
        default=timezone.localdate,
        help_text="BOM valid-from date.",
    )
    valid_to = models.DateField(null=True, blank=True, help_text="Blank = open-ended.")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["parent_product", "alternative", "code"]
        constraints = [
            models.UniqueConstraint(fields=("code",), name="f1_bomhdr_code_uq"),
            models.UniqueConstraint(
                fields=("parent_product", "alternative", "usage"),
                condition=models.Q(warehouse__isnull=True),
                name="f1_bomhdr_nopwh_uq",
            ),
            models.UniqueConstraint(
                fields=("parent_product", "warehouse", "alternative", "usage"),
                condition=models.Q(warehouse__isnull=False),
                name="f1_bomhdr_wh_uq",
            ),
        ]
        indexes = [
            models.Index(fields=("parent_product", "is_active"), name="f1_bomhdr_par_ix"),
        ]

    def __str__(self) -> str:
        wh = f" @{self.warehouse.code}" if self.warehouse_id else ""
        return f"{self.code} — {self.parent_product.code}{wh} (alt {self.alternative})"

    def clean(self) -> None:
        if self.code:
            self.code = self.code.strip()
        if not self.code:
            raise ValidationError({"code": "Code is required."})
        if self.name:
            self.name = self.name.strip()
        if not self.name:
            raise ValidationError({"name": "Name is required."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class ProductBomLine(models.Model):
    """SAP-style BOM line (STPO): position, component, quantity, UoM, scrap, optional line dates."""

    bom = models.ForeignKey(
        ProductBom,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    position = models.PositiveIntegerField(
        help_text="Item number (e.g. 10, 20, 30 — like STPO position).",
    )
    component_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="used_in_bom_lines",
    )
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Component quantity per 1 unit of header material.",
    )
    component_uom = models.ForeignKey(
        UnitOfMeasure,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bom_line_components",
        help_text="Component UoM; empty = use component material default UoM.",
    )
    scrap_percent = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        help_text="Component scrap % (SAP-style).",
    )
    item_text = models.TextField(blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["bom", "position"]
        constraints = [
            models.UniqueConstraint(fields=("bom", "position"), name="f1_bomln_bom_pos_uq"),
        ]
        indexes = [
            models.Index(fields=("bom", "component_product"), name="f1_bomln_bom_cmp_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.bom.code} / {self.position}: {self.component_product.code} × {self.quantity}"

    def clean(self) -> None:
        if self.bom_id and self.component_product_id:
            if self.bom.parent_product_id == self.component_product_id:
                raise ValidationError({"component_product": "Component must differ from header material."})

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)


class WarehouseStock(models.Model):
    """On-hand quantity per product (variant-less material) per warehouse."""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="warehouse_stocks",
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="product_stocks",
    )
    quantity_on_hand = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        default=Decimal("0"),
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("product", "warehouse"),
                name="f1_wstk_prod_wh_uq",
            ),
        ]
        indexes = [
            models.Index(fields=("warehouse", "product"), name="f1_wstk_wh_pr_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.product.code} @ {self.warehouse.code}: {self.quantity_on_hand}"


class ExchangeRate(models.Model):
    from_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="exchange_rates_from",
    )
    to_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name="exchange_rates_to",
    )
    rate = models.DecimalField(max_digits=18, decimal_places=8)
    effective_date = models.DateField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-effective_date", "from_currency", "to_currency"]
        constraints = [
            models.UniqueConstraint(
                fields=("from_currency", "to_currency", "effective_date"),
                name="f1_exrt_ft_ed_uq",
            ),
        ]
        indexes = [
            models.Index(fields=("is_active", "effective_date"), name="f1_exrt_is_ed_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.from_currency.code}→{self.to_currency.code} @ {self.effective_date}"

    def clean(self) -> None:
        if self.from_currency_id and self.to_currency_id and self.from_currency_id == self.to_currency_id:
            raise ValidationError({"to_currency": "From and to currency must differ."})
        if self.rate is not None and self.rate <= 0:
            raise ValidationError({"rate": "Rate must be positive."})


class UomConversion(models.Model):
    from_uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        related_name="conversion_sources",
    )
    to_uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.CASCADE,
        related_name="conversion_targets",
    )
    factor = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Multiply quantity in from_uom by this factor to get to_uom.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["from_uom", "to_uom"]
        verbose_name_plural = "UoM conversions"
        constraints = [
            models.UniqueConstraint(
                fields=("from_uom", "to_uom"),
                name="f1_uomc_ft_uq",
            ),
        ]
        indexes = [
            models.Index(fields=("is_active", "from_uom", "to_uom"), name="f1_uomc_is_ft_ix"),
        ]

    def __str__(self) -> str:
        return f"{self.from_uom.code} → {self.to_uom.code} (×{self.factor})"

    def clean(self) -> None:
        if self.from_uom_id and self.to_uom_id and self.from_uom_id == self.to_uom_id:
            raise ValidationError({"to_uom": "From and to UOM must differ."})
        if self.factor is not None and self.factor <= 0:
            raise ValidationError({"factor": "Factor must be positive."})
