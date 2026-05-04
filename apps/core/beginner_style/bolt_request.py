"""
Read common list parameters from a django-bolt ``request`` object.

Bolt stores parsed query values on ``request.query`` as a dict-like mapping.
"""

from __future__ import annotations

from typing import Any


def get_boolean_query_flag_is_true(request: Any, key: str) -> bool:
    """
    Return True when a query parameter is set to a common “truthy” string (1, true, yes).

    Used for optional flags like ``include_deleted=1`` on list endpoints.
    """
    qd = getattr(request, "query", None) or {}
    return (qd.get(key) or "").strip().lower() in ("1", "true", "yes")


def get_list_limit(request: Any) -> int:
    """
    Return ``limit`` for list endpoints (clamped between 1 and 100, default 50 on bad input).
    """
    qd = getattr(request, "query", None) or {}
    try:
        return min(100, max(1, int(qd.get("limit", "50"))))
    except ValueError:
        return 50


def get_list_offset(request: Any) -> int:
    """
    Return ``offset`` for list endpoints (never negative, default 0 on bad input).
    """
    qd = getattr(request, "query", None) or {}
    try:
        return max(0, int(qd.get("offset", "0")))
    except ValueError:
        return 0


def get_search_prefix(request: Any) -> str:
    """
    Return optional search prefix from ``q`` (trimmed). Empty string means “no filter”.
    """
    qd = getattr(request, "query", None) or {}
    return (qd.get("q") or "").strip()


def get_optional_int_from_query(request: Any, key: str) -> int | None:
    """
    Read an optional integer query parameter. Returns ``None`` if missing or not an int.
    """
    qd = getattr(request, "query", None) or {}
    raw = (qd.get(key) or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def get_list_pagination_for_request(request: Any) -> tuple[int, int, str]:
    """
    Convenience bundle: ``(limit, offset, search_prefix)`` for standard list endpoints.
    """
    return get_list_limit(request), get_list_offset(request), get_search_prefix(request)
