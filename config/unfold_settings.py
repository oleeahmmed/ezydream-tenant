"""django-unfold: theme, sidebar, dashboard hook (English UI)."""

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse_lazy


def unfold_environment(request):
    if settings.DEBUG:
        return ("DEV", "warning")
    return ("PROD", "success")


def _inter_font_stylesheet(request):
    return (
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    )


def _extra_unfold_css(request):
    return static("admin/unfold-extra.css")


UNFOLD = {
    "SITE_TITLE": "Ezydream ERP Admin",
    "SITE_HEADER": "Ezydream ERP",
    "SITE_SUBHEADER": "Multitenant control panel",
    "SITE_SYMBOL": "dataset",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "SHOW_UI_WARNINGS": True,
    "BORDER_RADIUS": "0.5rem",
    "ENVIRONMENT": unfold_environment,
    "DASHBOARD_CALLBACK": "config.dashboard_callback.build_admin_dashboard",
    "COLORS": {
        "primary": {
            "50": "oklch(98.4% .004 250)",
            "100": "oklch(96% .009 251)",
            "200": "oklch(92% .016 252)",
            "300": "oklch(86% .027 253)",
            "400": "oklch(72% .051 254)",
            "500": "oklch(55% .055 253)",
            "600": "oklch(45% .049 253)",
            "700": "oklch(38% .041 253)",
            "800": "oklch(30% .033 253)",
            "900": "oklch(22% .028 253)",
            "950": "oklch(16% .022 253)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-950)",
            "important-dark": "var(--color-base-50)",
        },
    },
    "STYLES": [
        _inter_font_stylesheet,
        _extra_unfold_css,
    ],
    "SCRIPTS": [],
    "COMMAND": {
        "search_models": True,
        "show_history": True,
        "search_callback": None,
    },
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Overview",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Tenants",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Tenant clients",
                        "icon": "apartment",
                        "link": reverse_lazy("admin:core_client_changelist"),
                    },
                    {
                        "title": "Domains",
                        "icon": "link",
                        "link": reverse_lazy("admin:core_domain_changelist"),
                    },
                ],
            },
            {
                "title": "Access control",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy(
                            "admin:tenant_auth_user_changelist"
                        ),
                    },
                    {
                        "title": "Groups",
                        "icon": "groups",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": "Foundation (ERP master data)",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Currencies",
                        "icon": "payments",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_currency_changelist"
                        ),
                    },
                    {
                        "title": "Exchange rates",
                        "icon": "currency_exchange",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_exchangerate_changelist"
                        ),
                    },
                    {
                        "title": "Tax types",
                        "icon": "receipt_long",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_taxtype_changelist"
                        ),
                    },
                    {
                        "title": "Tax rates",
                        "icon": "percent",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_taxrate_changelist"
                        ),
                    },
                    {
                        "title": "Units of measure",
                        "icon": "straighten",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_unitofmeasure_changelist"
                        ),
                    },
                    {
                        "title": "UoM conversions",
                        "icon": "swap_horiz",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_uomconversion_changelist"
                        ),
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_category_changelist"
                        ),
                    },
                    {
                        "title": "Products",
                        "icon": "inventory_2",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_product_changelist"
                        ),
                    },
                    {
                        "title": "Product variants",
                        "icon": "style",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_productvariant_changelist"
                        ),
                    },
                    {
                        "title": "BOM headers",
                        "icon": "difference",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_productbom_changelist"
                        ),
                    },
                    {
                        "title": "BOM lines",
                        "icon": "account_tree",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_productbomline_changelist"
                        ),
                    },
                    {
                        "title": "Warehouses",
                        "icon": "warehouse",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_warehouse_changelist"
                        ),
                    },
                    {
                        "title": "Warehouse stock",
                        "icon": "inventory",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_warehousestock_changelist"
                        ),
                    },
                    {
                        "title": "Customers",
                        "icon": "storefront",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_customer_changelist"
                        ),
                    },
                    {
                        "title": "Suppliers",
                        "icon": "local_shipping",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_supplier_changelist"
                        ),
                    },
                    {
                        "title": "Sales persons",
                        "icon": "badge",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_salesperson_changelist"
                        ),
                    },
                    {
                        "title": "Payment methods",
                        "icon": "credit_card",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_paymentmethod_changelist"
                        ),
                    },
                    {
                        "title": "Payment terms",
                        "icon": "event_repeat",
                        "link": reverse_lazy(
                            "admin:tenant_foundation_paymentterm_changelist"
                        ),
                    },
                ],
            },
        ],
    },
    "ACCOUNT": {
        "navigation": [
            {
                "title": "Change password",
                "link": reverse_lazy("admin:password_change"),
            },
        ],
    },
    "LOGIN": {
        "image": None,
        "redirect_after": None,
        "form": None,
    },
}
