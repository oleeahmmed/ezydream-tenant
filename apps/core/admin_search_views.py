"""
Staff-only JSON helpers for Django admin (session auth).

Bolt REST APIs use JWT; the admin UI uses cookies. These endpoints mirror the
list filters used by Bolt inventory/warehouse views and chart-of-accounts
lookups for finance/inventory admin, without embedding JWT in JavaScript.
"""

from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


def _int_clamp(raw: str | None, lo: int, hi: int, default: int) -> int:
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, n))


@staff_member_required
@require_GET
def erp_search_items(request: HttpRequest) -> JsonResponse:
    """Prefix search on ``OITM`` (same idea as ``GET /api/inventory/oitm``)."""
    from apps.inventory.models import OITM

    q = (request.GET.get("q") or "").strip()
    limit = _int_clamp(request.GET.get("limit"), 1, 100, 50)
    include_deleted = (request.GET.get("include_deleted") or "").strip().lower() in ("1", "true", "yes")

    qs = OITM.objects.select_related("ItmsGrpCod").order_by("ItemCode")
    if not include_deleted:
        qs = qs.filter(ValidFor="Y")
    if q:
        qs = qs.filter(Q(ItemCode__istartswith=q) | Q(ItemName__istartswith=q))
    rows = list(qs[:limit])

    return JsonResponse(
        {
            "items": [
                {
                    "ItemCode": o.ItemCode,
                    "ItemName": o.ItemName,
                    "ItmsGrpCod": o.ItmsGrpCod_id,
                }
                for o in rows
            ],
            "limit": limit,
        }
    )


@staff_member_required
@require_GET
def erp_search_warehouses(request: HttpRequest) -> JsonResponse:
    """Prefix search on active ``OWHS`` rows."""
    from apps.warehouse.models import OWHS

    q = (request.GET.get("q") or "").strip()
    limit = _int_clamp(request.GET.get("limit"), 1, 100, 50)
    qs = OWHS.objects.filter(Inactive="N").order_by("WhsCode")
    if q:
        qs = qs.filter(Q(WhsCode__istartswith=q) | Q(WhsName__istartswith=q))
    rows = list(qs[:limit])
    return JsonResponse(
        {"items": [{"WhsCode": r.WhsCode, "WhsName": r.WhsName} for r in rows], "limit": limit}
    )


@staff_member_required
@require_GET
def erp_search_gl_accounts(request: HttpRequest) -> JsonResponse:
    """Prefix search on ``OACT`` (G/L chart) for cash/bank/tax codes and BOM issue lines."""
    from apps.finance.models import OACT

    q = (request.GET.get("q") or "").strip()
    limit = _int_clamp(request.GET.get("limit"), 1, 100, 50)
    qs = OACT.objects.order_by("AcctCode")
    if q:
        qs = qs.filter(Q(AcctCode__istartswith=q) | Q(AcctName__istartswith=q))
    rows = list(qs[:limit])
    return JsonResponse(
        {
            "items": [{"AcctCode": r.AcctCode, "AcctName": r.AcctName} for r in rows],
            "limit": limit,
        }
    )
