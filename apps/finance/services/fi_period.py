"""Financial period (OFPR) checks for posting."""

from __future__ import annotations

from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError


def assert_open_fi_period(ref_date: date | None) -> None:
    """
    Ensure ``ref_date`` falls in at least one unlocked OFPR row.

    Skipped when ``FINANCE_ENFORCE_OFPR`` is False, or when no OFPR rows exist yet.
    """
    if ref_date is None:
        return
    if not getattr(settings, "FINANCE_ENFORCE_OFPR", True):
        return
    from apps.finance.models import OFPR

    if not OFPR.objects.exists():
        return
    ok = (
        OFPR.objects.filter(F_RefDate__lte=ref_date, T_RefDate__gte=ref_date)
        .exclude(PeriodStat__iexact="Locked")
        .exclude(PeriodStat__iexact="Closed")
        .exists()
    )
    if not ok:
        raise ValidationError(
            f"Posting date {ref_date} is not in an unlocked financial period (OFPR). "
            "Create or unlock a period, or set FINANCE_ENFORCE_OFPR=False."
        )
