"""
Small, explicit helpers for parsing finance API paths and query strings.

Bolt exposes query parameters on ``request.query``; see ``apps.core.beginner_style.bolt_request``
for shared limit/offset/search helpers.
"""

from __future__ import annotations


def normalize_budget_profit_center_path_segment(prc_code: str) -> str:
    """
    Budget lines store an empty profit center as ``""`` in the database, but URLs use ``"-"``.

    This converts the path segment back to the stored primary-key value.
    """
    stripped = prc_code.strip()
    return "" if stripped == "-" else stripped
