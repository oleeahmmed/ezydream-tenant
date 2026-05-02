"""Foundation — Unfold ``ModelAdmin`` + ``unfold.contrib.filters``."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,
    BooleanRadioFilter,
    RangeDateFilter,
)

from . import models as m


@admin.register(m.Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ("code", "name", "city", "country", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name", "city", "country")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name", "description")}),
        (_("Address"), {"fields": ("address_line1", "address_line2", "city", "state", "postal_code", "country")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("code", "name", "parent", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name")
    ordering = ("name",)
    autocomplete_fields = ("parent",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name", "description")}),
        (_("Hierarchy"), {"fields": ("parent",)}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.UnitOfMeasure)
class UnitOfMeasureAdmin(ModelAdmin):
    list_display = ("code", "name", "decimal_places", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name", "decimal_places")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.Currency)
class CurrencyAdmin(ModelAdmin):
    list_display = ("code", "name", "symbol", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name", "symbol")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.TaxType)
class TaxTypeAdmin(ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name", "description")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.TaxRate)
class TaxRateAdmin(ModelAdmin):
    list_display = ("tax_type", "rate_percent", "effective_from", "updated_at")
    list_filter = (("tax_type", AutocompleteSelectFilter),)
    search_fields = ("tax_type__code", "tax_type__name")
    ordering = ("-effective_from",)
    autocomplete_fields = ("tax_type",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Tax"), {"fields": ("tax_type", "rate_percent", "effective_from")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ("code", "name", "city", "currency", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (
        ("currency", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
    )
    search_fields = ("code", "name", "email", "phone")
    ordering = ("name",)
    list_select_related = ("currency",)
    autocomplete_fields = ("currency",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name")}),
        (_("Contact"), {"fields": ("email", "phone")}),
        (_("Address"), {"fields": ("address_line1", "address_line2", "city", "state", "postal_code", "country")}),
        (_("Defaults"), {"fields": ("currency",)}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ("code", "name", "city", "currency", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (
        ("currency", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
    )
    search_fields = ("code", "name", "email", "phone")
    ordering = ("name",)
    list_select_related = ("currency",)
    autocomplete_fields = ("currency",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name")}),
        (_("Contact"), {"fields": ("email", "phone")}),
        (_("Address"), {"fields": ("address_line1", "address_line2", "city", "state", "postal_code", "country")}),
        (_("Defaults"), {"fields": ("currency",)}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.SalesPerson)
class SalesPersonAdmin(ModelAdmin):
    list_display = ("code", "name", "email", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name", "email")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name")}),
        (_("Contact"), {"fields": ("email", "phone")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.PaymentMethod)
class PaymentMethodAdmin(ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.PaymentTerm)
class PaymentTermAdmin(ModelAdmin):
    list_display = ("code", "name", "days_until_due", "is_active", "updated_at")
    list_display_links = ("code", "name")
    list_filter = (("is_active", BooleanRadioFilter),)
    search_fields = ("code", "name")
    ordering = ("code",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name", "description")}),
        (_("Terms"), {"fields": ("days_until_due",)}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "code",
        "name",
        "category",
        "default_uom",
        "default_warehouse",
        "list_price",
        "is_active",
        "updated_at",
    )
    list_filter = (
        ("category", AutocompleteSelectFilter),
        ("default_uom", AutocompleteSelectFilter),
        ("default_warehouse", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
    )
    search_fields = ("code", "name", "description")
    ordering = ("name",)
    list_select_related = ("category", "default_uom", "default_warehouse")
    autocomplete_fields = ("category", "default_uom", "default_warehouse")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name", "description")}),
        (_("Classification"), {"fields": ("category", "default_uom", "default_warehouse")}),
        (_("Pricing / cost"), {"fields": ("default_unit_cost", "list_price")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    list_display = ("code", "product", "name", "barcode", "is_active", "updated_at")
    list_filter = (
        ("product", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
    )
    search_fields = ("code", "name", "barcode", "product__code", "product__name")
    ordering = ("product", "code")
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at", "updated_at")


class ProductBomLineInline(TabularInline):
    model = m.ProductBomLine
    extra = 0
    autocomplete_fields = ("component_product", "component_uom")
    fields = (
        "position",
        "component_product",
        "quantity",
        "component_uom",
        "scrap_percent",
        "item_text",
        "valid_from",
        "valid_to",
    )


@admin.register(m.ProductBom)
class ProductBomAdmin(ModelAdmin):
    list_display = (
        "code",
        "name",
        "parent_product",
        "warehouse",
        "usage",
        "alternative",
        "valid_from",
        "valid_to",
        "is_active",
        "updated_at",
    )
    list_display_links = ("code", "name")
    list_filter = (
        ("parent_product", AutocompleteSelectFilter),
        ("warehouse", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
    )
    search_fields = ("code", "name", "parent_product__code", "parent_product__name")
    ordering = ("parent_product", "alternative", "code")
    autocomplete_fields = ("parent_product", "warehouse")
    readonly_fields = ("created_at", "updated_at")
    inlines = (ProductBomLineInline,)
    fieldsets = (
        (_("Identification"), {"fields": ("code", "name")}),
        (_("Header material & plant"), {"fields": ("parent_product", "warehouse")}),
        (_("SAP-style keys"), {"fields": ("usage", "alternative", "valid_from", "valid_to")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.ProductBomLine)
class ProductBomLineAdmin(ModelAdmin):
    list_display = (
        "bom",
        "position",
        "component_product",
        "quantity",
        "component_uom",
        "scrap_percent",
        "updated_at",
    )
    list_filter = (
        ("bom", AutocompleteSelectFilter),
        ("component_product", AutocompleteSelectFilter),
    )
    autocomplete_fields = ("bom", "component_product", "component_uom")
    search_fields = ("bom__code", "component_product__code", "item_text")
    readonly_fields = ("created_at", "updated_at")


@admin.register(m.WarehouseStock)
class WarehouseStockAdmin(ModelAdmin):
    list_display = ("product", "warehouse", "quantity_on_hand", "updated_at")
    list_filter = (
        ("warehouse", AutocompleteSelectFilter),
        ("product", AutocompleteSelectFilter),
    )
    autocomplete_fields = ("product", "warehouse")
    search_fields = ("product__code", "warehouse__code")
    readonly_fields = ("updated_at",)


@admin.register(m.ExchangeRate)
class ExchangeRateAdmin(ModelAdmin):
    list_display = ("from_currency", "to_currency", "rate", "effective_date", "is_active", "updated_at")
    list_filter = (
        ("from_currency", AutocompleteSelectFilter),
        ("to_currency", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
        ("effective_date", RangeDateFilter),
    )
    search_fields = (
        "from_currency__code",
        "to_currency__code",
        "from_currency__name",
        "to_currency__name",
    )
    ordering = ("-effective_date",)
    list_select_related = ("from_currency", "to_currency")
    autocomplete_fields = ("from_currency", "to_currency")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Currencies"), {"fields": ("from_currency", "to_currency")}),
        (_("Rate"), {"fields": ("rate", "effective_date", "is_active")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(m.UomConversion)
class UomConversionAdmin(ModelAdmin):
    list_display = ("from_uom", "to_uom", "factor", "is_active", "updated_at")
    list_filter = (
        ("from_uom", AutocompleteSelectFilter),
        ("to_uom", AutocompleteSelectFilter),
        ("is_active", BooleanRadioFilter),
    )
    search_fields = ("from_uom__code", "to_uom__code")
    list_select_related = ("from_uom", "to_uom")
    autocomplete_fields = ("from_uom", "to_uom")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Units"), {"fields": ("from_uom", "to_uom", "factor")}),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )
