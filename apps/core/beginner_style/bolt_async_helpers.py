"""
Async helpers for Bolt ``APIView`` handlers.

Bolt view methods are ``async``; heavy synchronous work runs in a thread via
``sync_to_async``. These helpers use long, descriptive names instead of ``_bp_*``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError
from django_bolt.exceptions import BadRequest

from apps.businesspartner.services.bp_rollups import recalculate_bp_rollups


async def async_recalculate_business_partner_rollups_for_card_codes(*card_codes: str | None) -> None:
    """
    After finance or sales documents change a BP, refresh cached balances (``OCRD`` rollups).

    Skips empty codes; safe to pass old and new ``CardCode`` after a patch.
    """
    for raw in card_codes:
        trimmed = (raw or "").strip()
        if trimmed:
            await sync_to_async(recalculate_bp_rollups)(trimmed)


async def async_run_sync_callable_and_map_validation_error_to_bad_request(
    sync_callable: Callable[..., Any],
    *sync_args: Any,
) -> None:
    """
    Run a synchronous function in a worker thread.

    If it raises ``ValidationError`` (Django), convert to ``BadRequest`` so Bolt returns HTTP 400.
    """
    try:
        await sync_to_async(sync_callable)(*sync_args)
    except ValidationError as exc:
        msgs = list(getattr(exc, "messages", []))
        detail = "; ".join(str(m) for m in msgs) if msgs else str(exc)
        raise BadRequest(detail=detail) from exc
