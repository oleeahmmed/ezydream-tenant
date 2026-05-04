"""
Input validation for Bolt API views — raise ``BadRequest`` with readable English messages.

These mirror model rules but are used on raw request bodies before model instances exist.
"""

from __future__ import annotations

from django_bolt.exceptions import BadRequest


def require_yes_no_string_for_bolt(field_label: str, value: str | None) -> str:
    """
    Normalize a Y/N string from API input. Raises ``BadRequest`` if missing or invalid.
    """
    if value is None:
        raise BadRequest(detail=f"{field_label} required.")
    letter = (value or "N").strip().upper()[:1] or "N"
    if letter not in ("Y", "N"):
        raise BadRequest(detail=f"{field_label} must be Y or N.")
    return letter


def require_gl_group_mask_1_to_5(value: int) -> None:
    """Raise ``BadRequest`` if ``GroupMask`` is outside 1–5."""
    if int(value) not in (1, 2, 3, 4, 5):
        raise BadRequest(detail="GroupMask must be 1–5.")


def require_dimension_1_to_5(value: int) -> None:
    """Raise ``BadRequest`` if profit-center ``DimCode`` is outside 1–5."""
    if int(value) not in (1, 2, 3, 4, 5):
        raise BadRequest(detail="DimCode must be 1–5.")


def require_open_or_closed_document_status(raw: str | None) -> str:
    """
    Return ``O`` or ``C`` for payment ``DocStatus``. Raises ``BadRequest`` on invalid values.
    """
    letter = (raw or "O").strip().upper()[:1] or "O"
    if letter not in ("O", "C"):
        raise BadRequest(detail="DocStatus must be O or C.")
    return letter
