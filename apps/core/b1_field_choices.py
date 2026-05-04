"""
Single place for **stored codes** (what the DB keeps) and **human labels** (UI / admin).

- Integer constants: SAP B1–style ``OINM.TransType`` / ``OJDT.TransType`` (same names as before).
- ``CHOICE_GROUPS``: dropdown options for the frontend (``value`` must stay what the API saves).
- ``FIELD_TO_GROUP``: maps **JSON / form field name** → group id so one catalog drives many screens.
- ``FIELD_HINT_OVERRIDES_BY_LIST_PATH_PREFIX``: when the same field name means different things on
  different screens (e.g. ``TransType`` on journal vs inventory posting), merge hints using the
  document ``listPath`` prefix (longest match wins).

Old modules ``b1_inventory_transtype`` / ``b1_fi_journal_transtype`` are folded here — import from this file only.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Inventory OINM.TransType (subset used in code)
# ---------------------------------------------------------------------------
TRANS_GOODS_ISSUE = 13
TRANS_GOODS_RECEIPT = 14
TRANS_DELIVERY = 15
TRANS_GOODS_RETURN = 16
TRANS_GRPO = 20
TRANS_VENDOR_GOODS_RETURN = 21
TRANS_WAREHOUSE_TRANSFER = 67

# ---------------------------------------------------------------------------
# Finance OJDT.TransType markers (auto_journal)
# ---------------------------------------------------------------------------
JTRANS_AR_INVOICE = 13
JTRANS_AP_INVOICE = 18
JTRANS_OUTGOING_PAYMENT = 46
JTRANS_INCOMING_PAYMENT = 169


def _opt_str(value: str | int, label: str) -> dict[str, Any]:
    return {"value": value, "label": label}


def _opt_int(value: int, label: str) -> dict[str, Any]:
    return {"value": value, "label": label}


# --- Dropdown groups (``value`` = persisted form / DB value) ---

CHOICE_GROUPS: dict[str, list[dict[str, Any]]] = {
    "yes_no": [
        _opt_str("Y", "Yes"),
        _opt_str("N", "No"),
    ],
    "canceled_flag": [
        _opt_str("N", "Not canceled"),
        _opt_str("Y", "Canceled"),
    ],
    "inactive_flag": [
        _opt_str("N", "Active"),
        _opt_str("Y", "Inactive"),
    ],
    "doc_status_open_closed": [
        _opt_str("O", "Open"),
        _opt_str("C", "Closed"),
    ],
    "financial_period_stat": [
        _opt_str("Unlocked", "Unlocked"),
        _opt_str("Locked", "Locked"),
        _opt_str("Closed", "Closed"),
    ],
    "inventory_transtype": [
        _opt_int(TRANS_GOODS_ISSUE, "Goods issue"),
        _opt_int(TRANS_GOODS_RECEIPT, "Goods receipt"),
        _opt_int(TRANS_DELIVERY, "Delivery (out)"),
        _opt_int(TRANS_GOODS_RETURN, "Customer return (in)"),
        _opt_int(TRANS_GRPO, "Goods receipt PO"),
        _opt_int(TRANS_VENDOR_GOODS_RETURN, "Return to vendor"),
        _opt_int(TRANS_WAREHOUSE_TRANSFER, "Warehouse transfer"),
    ],
    "fi_journal_transtype": [
        _opt_int(JTRANS_AR_INVOICE, "A/R invoice"),
        _opt_int(JTRANS_AP_INVOICE, "A/P invoice"),
        _opt_int(JTRANS_OUTGOING_PAYMENT, "Outgoing payment"),
        _opt_int(JTRANS_INCOMING_PAYMENT, "Incoming payment"),
    ],
    # BP / OCRG (``apps.businesspartner.models``)
    "bp_group_type": [
        _opt_str("C", "Customer"),
        _opt_str("S", "Supplier"),
        _opt_str("B", "Customer & supplier"),
    ],
    "bp_card_type": [
        _opt_str("C", "Customer"),
        _opt_str("S", "Supplier"),
        _opt_str("L", "Lead"),
    ],
    "bp_address_type": [
        _opt_str("S", "Ship-to"),
        _opt_str("B", "Bill-to"),
    ],
    # Production BOM header (``validate_production_bom_tree_type``)
    "bom_tree_type": [
        _opt_str("P", "Production"),
        _opt_str("S", "Sales"),
        _opt_str("A", "Assembly"),
        _opt_str("T", "Template"),
    ],
    # OWOR.Status (``validate_production_order_status_planned_released_or_closed``)
    "production_order_status": [
        _opt_str("P", "Planned"),
        _opt_str("R", "Released"),
        _opt_str("L", "Closed"),
    ],
    # ITT1.IssueMeth (when exposed in API later)
    "bom_line_issue_method": [
        _opt_str("M", "Manual"),
        _opt_str("B", "Backflush"),
        _opt_str("L", "Mixed"),
    ],
    # OACT.GroupMask (1–5)
    "gl_account_group_mask": [
        _opt_int(1, "Assets"),
        _opt_int(2, "Liabilities"),
        _opt_int(3, "Equity"),
        _opt_int(4, "Revenue"),
        _opt_int(5, "Expenses"),
    ],
    # OPRC.DimCode (1–5)
    "profit_center_dim": [
        _opt_int(1, "Dimension 1"),
        _opt_int(2, "Dimension 2"),
        _opt_int(3, "Dimension 3"),
        _opt_int(4, "Dimension 4"),
        _opt_int(5, "Dimension 5"),
    ],
    # SAP B1–style object / base type (subset used with document lines; null in DB often omitted)
    "sap_base_object_type": [
        _opt_int(-1, "None"),
        _opt_int(2, "Business partner"),
        _opt_int(13, "Quotation"),
        _opt_int(15, "Delivery"),
        _opt_int(16, "Returns"),
        _opt_int(17, "Sales order"),
        _opt_int(18, "A/R invoice"),
        _opt_int(19, "A/R credit memo"),
        _opt_int(20, "Purchase order"),
        _opt_int(21, "Purchase quotation"),
        _opt_int(22, "Purchase request"),
        _opt_int(23, "Goods receipt PO"),
        _opt_int(59, "Goods issue"),
        _opt_int(67, "Stock transfer"),
        _opt_int(202, "Production order"),
    ],
    # ORCT / OVPM line allocation (``InvType`` — common SAP-style markers)
    "payment_line_inv_type": [
        _opt_int(0, "Manual / unspecified"),
        _opt_int(13, "Invoice"),
        _opt_int(14, "Credit note"),
        _opt_int(18, "A/P invoice"),
        _opt_int(19, "A/P credit memo"),
        _opt_int(24, "Return"),
        _opt_int(203, "Down payment"),
    ],
    # ISO 4217 — common document / BP currencies (value = stored code)
    "currency_iso": [
        _opt_str("USD", "USD — US Dollar"),
        _opt_str("EUR", "EUR — Euro"),
        _opt_str("GBP", "GBP — Pound Sterling"),
        _opt_str("BDT", "BDT — Bangladesh Taka"),
        _opt_str("INR", "INR — Indian Rupee"),
        _opt_str("SAR", "SAR — Saudi Riyal"),
        _opt_str("AED", "AED — UAE Dirham"),
        _opt_str("CNY", "CNY — Yuan Renminbi"),
        _opt_str("JPY", "JPY — Yen"),
        _opt_str("SGD", "SGD — Singapore Dollar"),
        _opt_str("HKD", "HKD — Hong Kong Dollar"),
        _opt_str("AUD", "AUD — Australian Dollar"),
        _opt_str("CAD", "CAD — Canadian Dollar"),
        _opt_str("CHF", "CHF — Swiss Franc"),
        _opt_str("SEK", "SEK — Swedish Krona"),
        _opt_str("NOK", "NOK — Norwegian Krone"),
        _opt_str("DKK", "DKK — Danish Krone"),
        _opt_str("PLN", "PLN — Zloty"),
        _opt_str("CZK", "CZK — Czech Koruna"),
        _opt_str("HUF", "HUF — Forint"),
        _opt_str("THB", "THB — Baht"),
        _opt_str("MYR", "MYR — Malaysian Ringgit"),
        _opt_str("IDR", "IDR — Rupiah"),
        _opt_str("PHP", "PHP — Philippine Peso"),
        _opt_str("VND", "VND — Dong"),
        _opt_str("ZAR", "ZAR — Rand"),
        _opt_str("EGP", "EGP — Egyptian Pound"),
        _opt_str("TRY", "TRY — Turkish Lira"),
        _opt_str("BRL", "BRL — Brazilian Real"),
        _opt_str("MXN", "MXN — Mexican Peso"),
        _opt_str("NZD", "NZD — New Zealand Dollar"),
        _opt_str("KRW", "KRW — Won"),
        _opt_str("TWD", "TWD — Taiwan Dollar"),
        _opt_str("PKR", "PKR — Pakistan Rupee"),
        _opt_str("LKR", "LKR — Sri Lanka Rupee"),
        _opt_str("NPR", "NPR — Nepalese Rupee"),
        _opt_str("RUB", "RUB — Russian Ruble"),
        _opt_str("UAH", "UAH — Hryvnia"),
        _opt_str("ILS", "ILS — Israeli Shekel"),
    ],
}


# Field name (Bolt JSON / typical form) → group id in CHOICE_GROUPS.
# Do **not** put ``TransType`` here — it differs between finance journal and inventory posting
# (same integer ``13`` means different things). Use ``FIELD_HINT_OVERRIDES_BY_LIST_PATH_PREFIX``.
FIELD_TO_GROUP: dict[str, str] = {
    "DocStatus": "doc_status_open_closed",
    "LineStatus": "doc_status_open_closed",
    "ValidFor": "yes_no",
    "Frozen": "yes_no",
    "Canceled": "canceled_flag",
    "InvntItem": "yes_no",
    "SalItem": "yes_no",
    "PrchseItem": "yes_no",
    "ByWh": "yes_no",
    "Locked": "yes_no",
    "Inactive": "inactive_flag",
    "PeriodStat": "financial_period_stat",
    # G/L master (OACT)
    "Postable": "yes_no",
    "LocCash": "yes_no",
    # Profit center (OPRC)
    "Active": "yes_no",
    # UoM (OUOM) — DataSource is Y/N in practice
    "DataSource": "yes_no",
    # Business partner
    "GroupType": "bp_group_type",
    "CardType": "bp_card_type",
    "AdresType": "bp_address_type",
    # BOM header (OITT.TreeType)
    "TreeType": "bom_tree_type",
    # BOM line (ITT1.IssueMeth) when exposed in API
    "IssueMeth": "bom_line_issue_method",
    # G/L account category & profit-center dimension
    "GroupMask": "gl_account_group_mask",
    "DimCode": "profit_center_dim",
    # Document / line linkage (sales, purchase, inventory lines)
    "BaseType": "sap_base_object_type",
    "TargetType": "sap_base_object_type",
    # Finance payment lines
    "InvType": "payment_line_inv_type",
    # Currency on documents / BP / company (stored as ISO code)
    "DocCur": "currency_iso",
    "Currency": "currency_iso",
    "MainCurncy": "currency_iso",
}


# (list_path without query string) prefix → extra field → group id (merged on top of FIELD_TO_GROUP).
FIELD_HINT_OVERRIDES_BY_LIST_PATH_PREFIX: tuple[tuple[str, dict[str, str]], ...] = (
    ("/api/finance/journal-entries", {"TransType": "fi_journal_transtype"}),
    ("/api/inventory/inventory-postings", {"TransType": "inventory_transtype"}),
    ("/api/production/production-orders", {"Status": "production_order_status"}),
)


def field_choice_catalog_for_api() -> dict[str, Any]:
    """Payload for ``GET /api/meta/field-choices`` (Bolt JSON)."""
    # Longest prefix first so e.g. ``/api/foo/bar`` wins over ``/api/foo`` if both exist later.
    overrides = [
        {"prefix": p, "hints": dict(h)}
        for p, h in sorted(FIELD_HINT_OVERRIDES_BY_LIST_PATH_PREFIX, key=lambda x: -len(x[0]))
    ]
    return {
        "groups": [{"id": gid, "options": opts} for gid, opts in CHOICE_GROUPS.items()],
        "fieldHints": dict(FIELD_TO_GROUP),
        "fieldHintsByListPathPrefix": overrides,
    }
