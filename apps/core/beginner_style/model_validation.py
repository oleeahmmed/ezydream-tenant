"""
Validation helpers for Django ``Model.clean()`` — raise ``ValidationError`` with clear messages.

These are used from model ``clean()`` methods so that invalid data never reaches the database.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError


def validate_yes_no_field(value: str, field_name: str) -> None:
    """
    Ensure a single-character flag is exactly ``Y`` or ``N``.

    ``field_name`` is used only inside the error message so the user knows which field failed.
    """
    if value not in ("Y", "N"):
        raise ValidationError({field_name: "Use Y or N."})


def validate_gl_group_mask_1_to_5(value: int) -> None:
    """
    Chart-of-accounts ``GroupMask`` must be 1–5 (SAP B1 style account categories).
    """
    if value not in (1, 2, 3, 4, 5):
        raise ValidationError({"GroupMask": "Use 1=Assets, 2=Liabilities, 3=Equity, 4=Revenue, 5=Expenses."})


def validate_dimension_1_to_5(value: int) -> None:
    """
    Profit-center ``DimCode`` must be between 1 and 5 (dimension number).
    """
    if value not in (1, 2, 3, 4, 5):
        raise ValidationError({"DimCode": "Dimension must be 1–5."})


def validate_finance_document_status_open_or_closed(value: str) -> None:
    """
    Document header ``DocStatus``: ``O`` (open) or ``C`` (closed).

    Same rule on finance payments, sales A/R, purchase A/P, and inventory documents.
    """
    if value not in ("O", "C"):
        raise ValidationError({"DocStatus": "Use O (open) or C (closed)."})


def validate_production_bom_tree_type(value: str) -> None:
    """BOM header ``TreeType``: P=Production, S=Sales, A=Assembly, T=Template."""
    if value not in ("P", "S", "A", "T"):
        raise ValidationError({"TreeType": "Use P (Production), S (Sales), A (Assembly), or T (Template)."})


def validate_production_order_status_planned_released_or_closed(value: str) -> None:
    """Production order ``Status``: P=Planned, R=Released, L=Closed."""
    if value not in ("P", "R", "L"):
        raise ValidationError({"Status": "Use P (Planned), R (Released), or L (Closed)."})


def validate_bom_line_issue_method_manual_backflush_or_mixed(value: str) -> None:
    """BOM line ``IssueMeth``: M=manual, B=backflush, L=mixed."""
    if value not in ("M", "B", "L"):
        raise ValidationError({"IssueMeth": "Use M (manual), B (backflush), or L (mixed)."})
