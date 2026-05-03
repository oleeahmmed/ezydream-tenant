"""
SAP Business One–style OINM.TransType values (subset used by document posting).

See SAP B1 DI / SDK inventory transaction type enumeration.
"""

from __future__ import annotations

# Outgoing delivery (sales) — reduces warehouse stock
TRANS_DELIVERY = 15
# Customer return — increases warehouse stock
TRANS_GOODS_RETURN = 16
# Goods Receipt PO (purchase)
TRANS_GRPO = 20
# Goods return to vendor (ORPD/ORPC-style)
TRANS_VENDOR_GOODS_RETURN = 21
# Goods issue (inventory)
TRANS_GOODS_ISSUE = 13
# Goods receipt (inventory)
TRANS_GOODS_RECEIPT = 14
# Inventory transfer (two OINM rows: out from + in to; both use type 67 in B1)
TRANS_WAREHOUSE_TRANSFER = 67
