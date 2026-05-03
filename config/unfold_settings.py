"""django-unfold (0.65.x): theme, sidebar, dashboard hook."""

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


def _nav_item(title: str, icon: str, app: str, model: str):
    return {
        "title": title,
        "icon": icon,
        "link": reverse_lazy(f"admin:{app}_{model}_changelist"),
    }


UNFOLD = {
    "SITE_TITLE": "Ezydream ERP Admin",
    "SITE_HEADER": "Ezydream ERP",
    "SITE_SUBHEADER": "Multitenant control panel",
    "SITE_SYMBOL": "speed",
    "SITE_URL": "/",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "SHOW_LANGUAGES": False,
    "ENVIRONMENT": unfold_environment,
    "DASHBOARD_CALLBACK": "config.dashboard_callback.build_admin_dashboard",
    "COLORS": {
        "primary": {
            "50": "252 254 235",
            "100": "247 252 213",
            "200": "238 248 178",
            "300": "226 242 142",
            "400": "208 234 106",
            "500": "196 216 46",
            "600": "168 184 42",
            "700": "140 154 35",
            "800": "112 123 28",
            "900": "84 92 21",
            "950": "63 69 16",
        },
        "font": {
            "subtle-light": "115 115 115",
            "default-light": "75 85 99",
            "dark-light": "55 65 81",
            "subtle-dark": "156 163 175",
            "default-dark": "209 213 219",
            "dark-dark": "243 244 246",
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
                        "link": reverse_lazy("admin:tenant_auth_user_changelist"),
                    },
                    {
                        "title": "Groups",
                        "icon": "groups",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
            {
                "title": "Warehouse",
                "separator": True,
                "collapsible": True,
                "items": [
                    _nav_item("Warehouses (OWHS)", "warehouse", "tenant_warehouse", "owhs"),
                ],
            },
            {
                "title": "Business partners",
                "separator": True,
                "collapsible": True,
                "items": [
                    _nav_item("BP groups (OCRG)", "groups", "tenant_businesspartner", "ocrg"),
                    _nav_item("Business partners (OCRD)", "contacts", "tenant_businesspartner", "ocrd"),
                ],
            },
            {
                "title": "Inventory",
                "separator": True,
                "collapsible": True,
                "items": [
                    _nav_item("Item groups (OITB)", "category", "tenant_inventory", "oitb"),
                    _nav_item("Items (OITM)", "inventory_2", "tenant_inventory", "oitm"),
                    _nav_item("Units of measure (OUOM)", "straighten", "tenant_inventory", "ouom"),
                    _nav_item("Transfer requests (OWTQ)", "swap_horiz", "tenant_inventory", "owtq"),
                    _nav_item("Stock transfers (OWTR)", "local_shipping", "tenant_inventory", "owtr"),
                    _nav_item("Goods receipts (OIGN)", "inbox", "tenant_inventory", "oign"),
                    _nav_item("Goods issues (OIGE)", "outbox", "tenant_inventory", "oige"),
                    _nav_item("Inventory postings (OINC)", "fact_check", "tenant_inventory", "oinc"),
                    _nav_item("Stock ledger (OINM)", "table_chart", "tenant_inventory", "oinm"),
                ],
            },
            {
                "title": "Sales (A/R)",
                "separator": True,
                "collapsible": True,
                "items": [
                    _nav_item("Quotations (OQUT)", "request_quote", "tenant_sales", "oqut"),
                    _nav_item("Orders (ORDR)", "shopping_cart", "tenant_sales", "ordr"),
                    _nav_item("Deliveries (ODLN)", "local_shipping", "tenant_sales", "odln"),
                    _nav_item("Returns (ORDN)", "assignment_return", "tenant_sales", "ordn"),
                    _nav_item("A/R invoices (OINV)", "receipt_long", "tenant_sales", "oinv"),
                ],
            },
            {
                "title": "Purchase (A/P)",
                "separator": True,
                "collapsible": True,
                "items": [
                    _nav_item("Purchase requests (OPRQ)", "playlist_add", "tenant_purchase", "oprq"),
                    _nav_item("Purchase orders (OPOR)", "shopping_bag", "tenant_purchase", "opor"),
                    _nav_item("Goods receipt PO (OPDN)", "inventory", "tenant_purchase", "opdn"),
                    _nav_item("Goods returns (ORPC)", "undo", "tenant_purchase", "orpc"),
                    _nav_item("A/P invoices (OPCH)", "description", "tenant_purchase", "opch"),
                ],
            },
            {
                "title": "Production",
                "separator": True,
                "collapsible": True,
                "items": [
                    _nav_item("BOM headers (OITT)", "account_tree", "tenant_production", "oitt"),
                    _nav_item("Production orders (OWOR)", "precision_manufacturing", "tenant_production", "owor"),
                ],
            },
            {
                "title": "Finance",
                "separator": True,
                "collapsible": True,
                "items": [
                    _nav_item("Chart of accounts (OACT)", "account_balance", "tenant_finance", "oact"),
                    _nav_item("Profit centers (OPRC)", "hub", "tenant_finance", "oprc"),
                    _nav_item("Journal entries (OJDT)", "edit_note", "tenant_finance", "ojdt"),
                    _nav_item("Incoming payments (ORCT)", "payments", "tenant_finance", "orct"),
                    _nav_item("Outgoing payments (OVPM)", "account_balance_wallet", "tenant_finance", "ovpm"),
                    _nav_item("Tax codes (OSTC)", "percent", "tenant_finance", "ostc"),
                    _nav_item("Financial periods (OFPR)", "calendar_month", "tenant_finance", "ofpr"),
                    _nav_item("Budget setup (OBGT)", "savings", "tenant_finance", "obgt"),
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
