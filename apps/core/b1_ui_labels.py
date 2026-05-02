"""
SAP Business One–style **human-readable** field labels for Django ``verbose_name``.

Technical DB / model attribute names stay SAP-style (e.g. ``ItemCode``, ``Dscription``);
these strings match how the B1 client presents fields in forms (Title Case, readable).

All values use ``gettext_lazy`` so admin and forms respect translations.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

# --- Document headers ---
INTERNAL_NO = _("Internal No.")
DOCUMENT_NO = _("No.")
BP_CODE = _("BP Code")
BP_NAME = _("BP Name")
STATUS = _("Status")
POSTING_DATE = _("Posting Date")
DOCUMENT_DATE = _("Document Date")
DUE_DATE = _("Due Date")
DELIVERY_DATE = _("Delivery Date")
DOCUMENT_TOTAL = _("Document Total")
TAX = _("Tax")
DISCOUNT_TOTAL = _("Discount Total")
BP_REFERENCE_NO = _("BP Reference No.")
CONTACT_PERSON = _("Contact Person")
CURRENCY = _("Currency")
REMARKS = _("Remarks")
COMMENTS = _("Comments")
SALES_EMPLOYEE = _("Sales Employee")
OWNER = _("Owner")
CREATED_BY = _("Created By")
REQUESTER = _("Requester")
CANCELED = _("Canceled")
VALID_FOR = _("Valid For")

# --- Document lines ---
PARENT_DOCUMENT = _("Document")
LINE_NO = _("Line No.")
ITEM_CODE = _("Item Code")
ITEM_NAME = _("Item Name")
ITEM_DESCRIPTION = _("Item Description")
QUANTITY = _("Quantity")
UNIT_PRICE = _("Unit Price")
WAREHOUSE = _("Warehouse")
FROM_WAREHOUSE = _("From Warehouse")
LINE_STATUS = _("Line Status")
OPEN_QUANTITY = _("Open Quantity")
LINE_TOTAL = _("Line Total")
DISCOUNT_PCT = _("Discount %")
BASE_TYPE = _("Base Type")
BASE_ENTRY = _("Base Entry")
BASE_LINE = _("Base Row")
TARGET_TYPE = _("Target Type")
TARGET_ENTRY = _("Target Document")
REFERENCE = _("Reference")
GL_ACCOUNT = _("G/L Account")

# --- Item groups & item master ---
ITEM_GROUP = _("Item Group")
ITEM_GROUP_NAME = _("Item Group Name")
INVENTORY_ITEM = _("Inventory Item")
IN_STOCK = _("In Stock")
COMMITTED = _("Committed")
ORDERED = _("Ordered")
MANAGE_BY_WAREHOUSE = _("Manage Item by Warehouse")
AVG_PRICE = _("Avg. Price")

# --- UoM ---
UOM_ENTRY = _("UoM Entry")
UOM_CODE = _("UoM Code")
UOM_NAME = _("UoM Name")
LOCKED = _("Locked")
DATA_SOURCE = _("Data Source")

# --- Warehouse (OWHS) ---
WAREHOUSE_CODE = _("Warehouse Code")
WAREHOUSE_NAME = _("Warehouse Name")
LOCATION = _("Location")
INACTIVE = _("Inactive")

# --- Inventory posting / ledger ---
COUNT_DATE = _("Count Date")
IN_QUANTITY = _("In Quantity")
OUT_QUANTITY = _("Out Quantity")
DIFFERENCE = _("Difference")
USER_REFERENCE = _("User Reference")
POSTING_DATE_TIME = _("Posting Date and Time")
TRANSACTION_TYPE = _("Transaction Type")
TRANSACTION_NO = _("Transaction No.")

# --- Production ---
PRODUCT_NO = _("Product No.")
BOM_CATEGORY = _("BOM Category")
BASE_QUANTITY = _("Base Quantity")
PRODUCTION_STATUS = _("Status")
PLANNED_QTY = _("Planned Quantity")
COMPLETED_QTY = _("Completed Quantity")
ISSUED_QTY = _("Issued Quantity")

# --- Finance: chart & dimensions ---
ACCOUNT_CODE = _("G/L Account")
ACCOUNT_NAME = _("Account Name")
BALANCE = _("Balance")
ACCOUNT_TYPE = _("Account Type")
FATHER_ACCOUNT = _("Father Account")
POSTING_ALLOWED = _("Posting Allowed")
CASH_ACCOUNT = _("Cash Account")
CASH_ACCOUNT_FLAG = _("Cash Account")
PROFIT_CENTER = _("Profit Center")
PROFIT_CENTER_NAME = _("Profit Center Name")
DIMENSION_NO = _("Dimension No.")
ACTIVE = _("Active")

# --- Journal ---
JOURNAL_MEMO = _("Memo")
JOURNAL_LINE_ID = _("Line ID")
SHORT_NAME = _("Short Name")
DEBIT = _("Debit")
CREDIT = _("Credit")
PROFIT_CENTER_CODE = _("Profit Center")

# --- Payments ---
CHECK_ACCOUNT = _("Check Account")
CASH_AMOUNT = _("Cash")
BANK_ACCOUNT = _("Bank Account")
BANK_TRANSFER = _("Bank Transfer")
APPLIED_AMOUNT = _("Applied Amount")
INVOICE_TYPE = _("Invoice Type")

# --- Tax (OSTC) ---
CODE = _("Code")
NAME = _("Name")
RATE = _("Rate")
TAX_ACCOUNT = _("Tax Account")

# --- Periods & budget ---
SUBPERIOD_CODE = _("Subperiod Code")
PERIOD_FROM = _("Period From")
PERIOD_TO = _("Period To")
PERIOD_STATUS = _("Period Status")
BUDGET_TOTAL = _("Budget Total")
MONTH = _("Month")
PLANNED_AMOUNT = _("Planned Amount")
