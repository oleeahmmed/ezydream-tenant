"""
SAP Business One–style OJDT.TransType values for automatic journal headers.

Mirrors common B1 object / journal source types (subset used by auto_journal).
"""

from __future__ import annotations

# A/R Invoice (OINV)
JTRANS_AR_INVOICE = 13
# A/P Invoice (OPCH)
JTRANS_AP_INVOICE = 18
# Incoming payment (ORCT) — B1 object-type style marker on OJDT
JTRANS_INCOMING_PAYMENT = 169
# Outgoing payment (OVPM)
JTRANS_OUTGOING_PAYMENT = 46
