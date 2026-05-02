"""
Bolt API: foundation masters — prefix search (``q``) on codes / names.

Bearer **access** JWT required (same as ``/api/auth/me``).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Annotated, Any, TypeVar

from asgiref.sync import sync_to_async
from django.db import IntegrityError, models
from django.db.models import Q
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import HTTPException, Unauthorized
from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested
from django_bolt.views import APIView

from apps.foundation import models as fm

_P = "/api/foundation"
_MAX_LIMIT = 100
_DEFAULT_LIMIT = 50

M = TypeVar("M", bound=models.Model)


def _u(s: str) -> str:
    return f"{_P}{s}"


def _access(request: Any) -> None:
    ctx = (request.get("auth") if hasattr(request, "get") else None) or {}
    claims = ctx.get("auth_claims") or {}
    if claims.get("typ") not in (None, "access"):
        raise Unauthorized(detail="Use access token, not refresh")


def _parse_query(request: Any) -> tuple[int, int, str, bool]:
    qd = getattr(request, "query", None) or {}
    try:
        limit = min(_MAX_LIMIT, max(1, int(qd.get("limit", str(_DEFAULT_LIMIT)))))
    except ValueError:
        limit = _DEFAULT_LIMIT
    try:
        offset = max(0, int(qd.get("offset", "0")))
    except ValueError:
        offset = 0
    q = (qd.get("q") or "").strip()
    active_only = (qd.get("active_only") or "1").strip().lower() in ("1", "true", "yes", "")
    return limit, offset, q, active_only


@sync_to_async
def _slice_qs(qs: models.QuerySet[M], start: int, end: int) -> list[M]:
    return list(qs[start:end])


def _prefix_on(
    qs: models.QuerySet,
    q: str,
    active_only: bool,
    *,
    active_field: str = "is_active",
    or_pairs: list[tuple[str, str]],
) -> models.QuerySet:
    if active_only:
        qs = qs.filter(**{f"{active_field}": True})
    if q:
        cond = Q()
        for a, b in or_pairs:
            cond |= Q(**{f"{a}__istartswith": q}) | Q(**{f"{b}__istartswith": q})
        qs = qs.filter(cond)
    return qs


def _bad(detail: str) -> None:
    raise HTTPException(status_code=400, detail=detail)


# --- serializers ---


class MasterRowOut(Serializer):
    id: int
    code: str
    name: str
    is_active: bool


class MasterListOut(Serializer):
    items: Annotated[list[MasterRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class MasterCreateIn(Serializer):
    code: str
    name: str
    is_active: bool = field(default=True)


class TaxTypeCreateIn(Serializer):
    code: str
    name: str
    description: str = field(default="")
    is_active: bool = field(default=True)


class CurrencyRowOut(Serializer):
    id: int
    code: str
    name: str
    is_active: bool
    symbol: str = field(default="")


class CurrencyListOut(Serializer):
    items: Annotated[list[CurrencyRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class CurrencyCreateIn(Serializer):
    code: str
    name: str
    symbol: str = field(default="")
    is_active: bool = field(default=True)


class TaxRateRowOut(Serializer):
    id: int
    tax_type_id: int
    rate_percent: str
    effective_from: date


class TaxRateListOut(Serializer):
    items: Annotated[list[TaxRateRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class TaxRateCreateIn(Serializer):
    tax_type_id: int
    rate_percent: str
    effective_from: date


class UomCreateIn(Serializer):
    code: str
    name: str
    decimal_places: int = field(default=0)
    is_active: bool = field(default=True)


class CategoryRowOut(Serializer):
    id: int
    code: str
    name: str
    is_active: bool
    parent_id: int | None = field(default=None)


class CategoryListOut(Serializer):
    items: Annotated[list[CategoryRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class CategoryCreateIn(Serializer):
    code: str
    name: str
    parent_id: int | None = field(default=None)
    is_active: bool = field(default=True)


class WarehouseRowOut(Serializer):
    id: int
    code: str
    name: str
    is_active: bool
    city: str = field(default="")
    country: str = field(default="")


class WarehouseListOut(Serializer):
    items: Annotated[list[WarehouseRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class WarehouseCreateIn(Serializer):
    code: str
    name: str
    description: str = field(default="")
    address_line1: str = field(default="")
    address_line2: str = field(default="")
    city: str = field(default="")
    state: str = field(default="")
    postal_code: str = field(default="")
    country: str = field(default="")
    is_active: bool = field(default=True)


class PaymentTermRowOut(Serializer):
    id: int
    code: str
    name: str
    is_active: bool
    days_until_due: int | None = field(default=None)


class PaymentTermListOut(Serializer):
    items: Annotated[list[PaymentTermRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class PaymentTermCreateIn(Serializer):
    code: str
    name: str
    days_until_due: int | None = field(default=None)
    description: str = field(default="")
    is_active: bool = field(default=True)


class SalesPersonRowOut(Serializer):
    id: int
    code: str
    name: str
    is_active: bool
    email: str = field(default="")


class SalesPersonListOut(Serializer):
    items: Annotated[list[SalesPersonRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class SalesPersonCreateIn(Serializer):
    code: str
    name: str
    email: str = field(default="")
    phone: str = field(default="")
    is_active: bool = field(default=True)


class PartyRowOut(Serializer):
    """Party master: ``code`` + ``name`` (SAP-style account + name1)."""

    id: int
    code: str
    name: str
    is_active: bool
    currency_id: int | None = field(default=None)
    phone: str = field(default="")
    email: str = field(default="")


class PartyListOut(Serializer):
    items: Annotated[list[PartyRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class PartyCreateIn(Serializer):
    code: str
    name: str
    currency_id: int | None = field(default=None)
    phone: str = field(default="")
    email: str = field(default="")
    is_active: bool = field(default=True)


class ProductRowOut(Serializer):
    id: int
    code: str
    name: str
    is_active: bool
    category_id: int | None = field(default=None)
    default_uom_id: int | None = field(default=None)
    default_warehouse_id: int | None = field(default=None)
    default_unit_cost: str
    list_price: str


class ProductListOut(Serializer):
    items: Annotated[list[ProductRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class ProductCreateIn(Serializer):
    code: str
    name: str
    description: str = field(default="")
    category_id: int | None = field(default=None)
    default_uom_id: int | None = field(default=None)
    default_warehouse_id: int | None = field(default=None)
    default_unit_cost: str = field(default="0")
    list_price: str = field(default="0")
    is_active: bool = field(default=True)


class ExchangeRateRowOut(Serializer):
    id: int
    from_currency_id: int
    to_currency_id: int
    from_code: str
    to_code: str
    rate: str
    effective_date: date
    is_active: bool


class ExchangeRateListOut(Serializer):
    items: Annotated[list[ExchangeRateRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class ExchangeRateCreateIn(Serializer):
    from_currency_id: int
    to_currency_id: int
    rate: str
    effective_date: date
    is_active: bool = field(default=True)


class UomConversionRowOut(Serializer):
    id: int
    from_uom_id: int
    to_uom_id: int
    from_code: str
    to_code: str
    factor: str
    is_active: bool


class UomConversionListOut(Serializer):
    items: Annotated[list[UomConversionRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class UomConversionCreateIn(Serializer):
    from_uom_id: int
    to_uom_id: int
    factor: str
    is_active: bool = field(default=True)


class ProductVariantRowOut(Serializer):
    id: int
    product_id: int
    product_code: str
    code: str
    name: str
    barcode: str
    is_active: bool


class ProductVariantListOut(Serializer):
    items: Annotated[list[ProductVariantRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class ProductVariantCreateIn(Serializer):
    product_id: int
    code: str
    name: str
    barcode: str = field(default="")
    is_active: bool = field(default=True)


class BomRowOut(Serializer):
    id: int
    code: str
    name: str
    parent_product_id: int
    warehouse_id: int | None = field(default=None)
    usage: str
    alternative: int
    valid_from: date
    valid_to: date | None = field(default=None)
    is_active: bool


class BomListOut(Serializer):
    items: Annotated[list[BomRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class BomCreateIn(Serializer):
    code: str
    name: str
    parent_product_id: int
    warehouse_id: int | None = field(default=None)
    usage: str = field(default="1")
    alternative: int = field(default=1)
    valid_from: date | None = field(default=None)
    valid_to: date | None = field(default=None)
    is_active: bool = field(default=True)


class BomLineRowOut(Serializer):
    id: int
    bom_id: int
    parent_product_id: int
    position: int
    component_product_id: int
    quantity: str
    component_uom_id: int | None = field(default=None)
    scrap_percent: str
    item_text: str
    valid_from: date | None = field(default=None)
    valid_to: date | None = field(default=None)


class BomLineListOut(Serializer):
    items: Annotated[list[BomLineRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class BomLineCreateIn(Serializer):
    bom_id: int
    position: int
    component_product_id: int
    quantity: str
    component_uom_id: int | None = field(default=None)
    scrap_percent: str = field(default="0")
    item_text: str = field(default="")
    valid_from: date | None = field(default=None)
    valid_to: date | None = field(default=None)


class StockRowOut(Serializer):
    id: int
    product_id: int
    product_code: str
    warehouse_id: int
    warehouse_code: str
    quantity_on_hand: str


class StockListOut(Serializer):
    items: Annotated[list[StockRowOut], Nested(max_items=_MAX_LIMIT)]
    limit: int
    offset: int


class StockCreateIn(Serializer):
    product_id: int
    warehouse_id: int
    quantity_on_hand: str = field(default="0")


# --- views ---


class CurrenciesView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> CurrencyListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.Currency.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return CurrencyListOut(
            items=[
                CurrencyRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    symbol=o.symbol or "",
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: CurrencyCreateIn) -> CurrencyRowOut:
        _access(self.request)
        o = fm.Currency(
            code=data.code.strip(),
            name=data.name.strip(),
            symbol=(data.symbol or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate currency code.")
        return CurrencyRowOut(
            id=o.pk, code=o.code, name=o.name, is_active=o.is_active, symbol=o.symbol or ""
        )


class TaxTypesView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> MasterListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.TaxType.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return MasterListOut(
            items=[MasterRowOut(id=o.pk, code=o.code, name=o.name, is_active=o.is_active) for o in rows],
            limit=lim,
            offset=off,
        )

    async def post(self, data: TaxTypeCreateIn) -> MasterRowOut:
        _access(self.request)
        o = fm.TaxType(
            code=data.code.strip(),
            name=data.name.strip(),
            description=(data.description or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate tax type code.")
        return MasterRowOut(id=o.pk, code=o.code, name=o.name, is_active=o.is_active)


class TaxRatesView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> TaxRateListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.TaxRate.objects.select_related("tax_type").order_by("-effective_from", "tax_type__code")
        if q:
            qs = qs.filter(Q(tax_type__code__istartswith=q) | Q(tax_type__name__istartswith=q))
        rows = await _slice_qs(qs, off, off + lim)
        return TaxRateListOut(
            items=[
                TaxRateRowOut(
                    id=o.pk,
                    tax_type_id=o.tax_type_id,
                    rate_percent=str(o.rate_percent),
                    effective_from=o.effective_from,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: TaxRateCreateIn) -> TaxRateRowOut:
        _access(self.request)
        if not await fm.TaxType.objects.filter(pk=data.tax_type_id).aexists():
            _bad("Invalid tax_type_id.")
        o = fm.TaxRate(
            tax_type_id=data.tax_type_id,
            rate_percent=Decimal(str(data.rate_percent)),
            effective_from=data.effective_from,
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate rate for this tax type and effective_from.")
        return TaxRateRowOut(
            id=o.pk,
            tax_type_id=o.tax_type_id,
            rate_percent=str(o.rate_percent),
            effective_from=o.effective_from,
        )


class UnitsOfMeasureView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> MasterListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.UnitOfMeasure.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return MasterListOut(
            items=[MasterRowOut(id=o.pk, code=o.code, name=o.name, is_active=o.is_active) for o in rows],
            limit=lim,
            offset=off,
        )

    async def post(self, data: UomCreateIn) -> MasterRowOut:
        _access(self.request)
        o = fm.UnitOfMeasure(
            code=data.code.strip(),
            name=data.name.strip(),
            decimal_places=max(0, min(10, int(data.decimal_places))),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate UoM code.")
        return MasterRowOut(id=o.pk, code=o.code, name=o.name, is_active=o.is_active)


class CategoriesView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> CategoryListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.Category.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return CategoryListOut(
            items=[
                CategoryRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    parent_id=o.parent_id,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: CategoryCreateIn) -> CategoryRowOut:
        _access(self.request)
        pid = data.parent_id
        if pid is not None and not await fm.Category.objects.filter(pk=pid).aexists():
            _bad("Invalid parent_id.")
        o = fm.Category(
            code=data.code.strip(),
            name=data.name.strip(),
            parent_id=pid,
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate category code.")
        return CategoryRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            is_active=o.is_active,
            parent_id=o.parent_id,
        )


class WarehousesView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> WarehouseListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.Warehouse.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return WarehouseListOut(
            items=[
                WarehouseRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    city=o.city or "",
                    country=o.country or "",
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: WarehouseCreateIn) -> WarehouseRowOut:
        _access(self.request)
        o = fm.Warehouse(
            code=data.code.strip(),
            name=data.name.strip(),
            description=(data.description or "").strip(),
            address_line1=(data.address_line1 or "").strip(),
            address_line2=(data.address_line2 or "").strip(),
            city=(data.city or "").strip(),
            state=(data.state or "").strip(),
            postal_code=(data.postal_code or "").strip(),
            country=(data.country or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate warehouse code.")
        return WarehouseRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            is_active=o.is_active,
            city=o.city or "",
            country=o.country or "",
        )


class PaymentMethodsView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> MasterListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.PaymentMethod.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return MasterListOut(
            items=[MasterRowOut(id=o.pk, code=o.code, name=o.name, is_active=o.is_active) for o in rows],
            limit=lim,
            offset=off,
        )

    async def post(self, data: MasterCreateIn) -> MasterRowOut:
        _access(self.request)
        o = fm.PaymentMethod(code=data.code.strip(), name=data.name.strip(), is_active=bool(data.is_active))
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate payment method code.")
        return MasterRowOut(id=o.pk, code=o.code, name=o.name, is_active=o.is_active)


class PaymentTermsView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> PaymentTermListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.PaymentTerm.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return PaymentTermListOut(
            items=[
                PaymentTermRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    days_until_due=o.days_until_due,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: PaymentTermCreateIn) -> PaymentTermRowOut:
        _access(self.request)
        o = fm.PaymentTerm(
            code=data.code.strip(),
            name=data.name.strip(),
            days_until_due=data.days_until_due,
            description=(data.description or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate payment term code.")
        return PaymentTermRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            is_active=o.is_active,
            days_until_due=o.days_until_due,
        )


class SalesPersonsView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> SalesPersonListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.SalesPerson.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return SalesPersonListOut(
            items=[
                SalesPersonRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    email=o.email or "",
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: SalesPersonCreateIn) -> SalesPersonRowOut:
        _access(self.request)
        o = fm.SalesPerson(
            code=data.code.strip(),
            name=data.name.strip(),
            email=(data.email or "").strip(),
            phone=(data.phone or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate sales person code.")
        return SalesPersonRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            is_active=o.is_active,
            email=o.email or "",
        )


class SuppliersView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> PartyListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.Supplier.objects.all().order_by("code")
        qs = _prefix_on(
            qs,
            q,
            active_only,
            or_pairs=[("code", "name")],
        )
        rows = await _slice_qs(qs, off, off + lim)
        return PartyListOut(
            items=[
                PartyRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    currency_id=o.currency_id,
                    phone=o.phone or "",
                    email=o.email or "",
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: PartyCreateIn) -> PartyRowOut:
        _access(self.request)
        cid = data.currency_id
        if cid is not None and not await fm.Currency.objects.filter(pk=cid).aexists():
            _bad("Invalid currency_id.")
        o = fm.Supplier(
            code=data.code.strip(),
            name=data.name.strip(),
            currency_id=cid,
            phone=(data.phone or "").strip(),
            email=(data.email or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate supplier code.")
        return PartyRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            is_active=o.is_active,
            currency_id=o.currency_id,
            phone=o.phone or "",
            email=o.email or "",
        )


class CustomersView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> PartyListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.Customer.objects.all().order_by("code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("code", "name")])
        rows = await _slice_qs(qs, off, off + lim)
        return PartyListOut(
            items=[
                PartyRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    currency_id=o.currency_id,
                    phone=o.phone or "",
                    email=o.email or "",
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: PartyCreateIn) -> PartyRowOut:
        _access(self.request)
        cid = data.currency_id
        if cid is not None and not await fm.Currency.objects.filter(pk=cid).aexists():
            _bad("Invalid currency_id.")
        o = fm.Customer(
            code=data.code.strip(),
            name=data.name.strip(),
            currency_id=cid,
            phone=(data.phone or "").strip(),
            email=(data.email or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate customer code.")
        return PartyRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            is_active=o.is_active,
            currency_id=o.currency_id,
            phone=o.phone or "",
            email=o.email or "",
        )


class ProductsView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ProductListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.Product.objects.select_related("category", "default_uom", "default_warehouse").order_by("code")
        if active_only:
            qs = qs.filter(is_active=True)
        if q:
            qs = qs.filter(
                Q(code__istartswith=q)
                | Q(name__istartswith=q)
                | Q(category__code__istartswith=q)
                | Q(default_uom__code__istartswith=q)
            )
        rows = await _slice_qs(qs, off, off + lim)
        return ProductListOut(
            items=[
                ProductRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    is_active=o.is_active,
                    category_id=o.category_id,
                    default_uom_id=o.default_uom_id,
                    default_warehouse_id=o.default_warehouse_id,
                    default_unit_cost=str(o.default_unit_cost),
                    list_price=str(o.list_price),
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: ProductCreateIn) -> ProductRowOut:
        _access(self.request)
        if data.category_id is not None and not await fm.Category.objects.filter(pk=data.category_id).aexists():
            _bad("Invalid category_id.")
        if data.default_uom_id is not None and not await fm.UnitOfMeasure.objects.filter(pk=data.default_uom_id).aexists():
            _bad("Invalid default_uom_id.")
        if data.default_warehouse_id is not None and not await fm.Warehouse.objects.filter(pk=data.default_warehouse_id).aexists():
            _bad("Invalid default_warehouse_id.")
        o = fm.Product(
            code=data.code.strip(),
            name=data.name.strip(),
            description=(data.description or "").strip(),
            category_id=data.category_id,
            default_uom_id=data.default_uom_id,
            default_warehouse_id=data.default_warehouse_id,
            default_unit_cost=Decimal(str(data.default_unit_cost or "0")),
            list_price=Decimal(str(data.list_price or "0")),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate product code.")
        return ProductRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            is_active=o.is_active,
            category_id=o.category_id,
            default_uom_id=o.default_uom_id,
            default_warehouse_id=o.default_warehouse_id,
            default_unit_cost=str(o.default_unit_cost),
            list_price=str(o.list_price),
        )


class ExchangeRatesView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ExchangeRateListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.ExchangeRate.objects.select_related("from_currency", "to_currency").order_by(
            "-effective_date", "from_currency__code", "to_currency__code"
        )
        if active_only:
            qs = qs.filter(is_active=True)
        if q:
            qs = qs.filter(
                Q(from_currency__code__istartswith=q)
                | Q(to_currency__code__istartswith=q)
                | Q(from_currency__name__istartswith=q)
                | Q(to_currency__name__istartswith=q)
            )
        rows = await _slice_qs(qs, off, off + lim)
        return ExchangeRateListOut(
            items=[
                ExchangeRateRowOut(
                    id=o.pk,
                    from_currency_id=o.from_currency_id,
                    to_currency_id=o.to_currency_id,
                    from_code=o.from_currency.code,
                    to_code=o.to_currency.code,
                    rate=str(o.rate),
                    effective_date=o.effective_date,
                    is_active=o.is_active,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: ExchangeRateCreateIn) -> ExchangeRateRowOut:
        _access(self.request)
        if data.from_currency_id == data.to_currency_id:
            _bad("from_currency_id and to_currency_id must differ.")
        fc = await fm.Currency.objects.filter(pk=data.from_currency_id).afirst()
        tc = await fm.Currency.objects.filter(pk=data.to_currency_id).afirst()
        if not fc or not tc:
            _bad("Invalid currency id.")
        o = fm.ExchangeRate(
            from_currency_id=data.from_currency_id,
            to_currency_id=data.to_currency_id,
            rate=Decimal(str(data.rate)),
            effective_date=data.effective_date,
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate rate for same pair and effective_date.")
        await o.arefresh_from_db()
        return ExchangeRateRowOut(
            id=o.pk,
            from_currency_id=o.from_currency_id,
            to_currency_id=o.to_currency_id,
            from_code=fc.code,
            to_code=tc.code,
            rate=str(o.rate),
            effective_date=o.effective_date,
            is_active=o.is_active,
        )


class UomConversionsView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> UomConversionListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.UomConversion.objects.select_related("from_uom", "to_uom").order_by("from_uom__code", "to_uom__code")
        qs = _prefix_on(qs, q, active_only, or_pairs=[("from_uom__code", "to_uom__code")])
        rows = await _slice_qs(qs, off, off + lim)
        return UomConversionListOut(
            items=[
                UomConversionRowOut(
                    id=o.pk,
                    from_uom_id=o.from_uom_id,
                    to_uom_id=o.to_uom_id,
                    from_code=o.from_uom.code,
                    to_code=o.to_uom.code,
                    factor=str(o.factor),
                    is_active=o.is_active,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: UomConversionCreateIn) -> UomConversionRowOut:
        _access(self.request)
        if data.from_uom_id == data.to_uom_id:
            _bad("from_uom_id and to_uom_id must differ.")
        fu = await fm.UnitOfMeasure.objects.filter(pk=data.from_uom_id).afirst()
        tu = await fm.UnitOfMeasure.objects.filter(pk=data.to_uom_id).afirst()
        if not fu or not tu:
            _bad("Invalid UoM id.")
        o = fm.UomConversion(
            from_uom_id=data.from_uom_id,
            to_uom_id=data.to_uom_id,
            factor=Decimal(str(data.factor)),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate conversion for this from/to pair.")
        return UomConversionRowOut(
            id=o.pk,
            from_uom_id=o.from_uom_id,
            to_uom_id=o.to_uom_id,
            from_code=fu.code,
            to_code=tu.code,
            factor=str(o.factor),
            is_active=o.is_active,
        )


class ProductVariantsView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ProductVariantListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.ProductVariant.objects.select_related("product").order_by("product__code", "code")
        if active_only:
            qs = qs.filter(is_active=True)
        if q:
            qs = qs.filter(
                Q(code__istartswith=q)
                | Q(name__istartswith=q)
                | Q(product__code__istartswith=q)
                | Q(product__name__istartswith=q)
            )
        rows = await _slice_qs(qs, off, off + lim)
        return ProductVariantListOut(
            items=[
                ProductVariantRowOut(
                    id=o.pk,
                    product_id=o.product_id,
                    product_code=o.product.code,
                    code=o.code,
                    name=o.name,
                    barcode=o.barcode or "",
                    is_active=o.is_active,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: ProductVariantCreateIn) -> ProductVariantRowOut:
        _access(self.request)
        if not await fm.Product.objects.filter(pk=data.product_id).aexists():
            _bad("Invalid product_id.")
        o = fm.ProductVariant(
            product_id=data.product_id,
            code=data.code.strip(),
            name=data.name.strip(),
            barcode=(data.barcode or "").strip(),
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate variant code.")
        p = await fm.Product.objects.aget(pk=o.product_id)
        return ProductVariantRowOut(
            id=o.pk,
            product_id=o.product_id,
            product_code=p.code,
            code=o.code,
            name=o.name,
            barcode=o.barcode or "",
            is_active=o.is_active,
        )


class ProductBomsView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BomListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.ProductBom.objects.select_related("parent_product", "warehouse").order_by(
            "parent_product__code", "alternative", "code"
        )
        if active_only:
            qs = qs.filter(is_active=True)
        if q:
            qs = qs.filter(
                Q(code__istartswith=q)
                | Q(name__istartswith=q)
                | Q(parent_product__code__istartswith=q)
                | Q(parent_product__name__istartswith=q)
            )
        rows = await _slice_qs(qs, off, off + lim)
        return BomListOut(
            items=[
                BomRowOut(
                    id=o.pk,
                    code=o.code,
                    name=o.name,
                    parent_product_id=o.parent_product_id,
                    warehouse_id=o.warehouse_id,
                    usage=o.usage,
                    alternative=int(o.alternative),
                    valid_from=o.valid_from,
                    valid_to=o.valid_to,
                    is_active=o.is_active,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: BomCreateIn) -> BomRowOut:
        _access(self.request)
        if not await fm.Product.objects.filter(pk=data.parent_product_id).aexists():
            _bad("Invalid parent_product_id.")
        wid = data.warehouse_id
        if wid is not None and not await fm.Warehouse.objects.filter(pk=wid).aexists():
            _bad("Invalid warehouse_id.")
        usage = ((data.usage or "1").strip()[:1] or "1")
        if usage not in {"1", "2", "3"}:
            _bad("Invalid usage (use 1=production, 2=costing, 3=engineering).")
        try:
            alt = max(1, int(data.alternative))
        except (TypeError, ValueError):
            _bad("Invalid alternative.")
        vf = data.valid_from if data.valid_from is not None else date.today()
        o = fm.ProductBom(
            code=data.code.strip(),
            name=data.name.strip(),
            parent_product_id=data.parent_product_id,
            warehouse_id=wid,
            usage=usage,
            alternative=alt,
            valid_from=vf,
            valid_to=data.valid_to,
            is_active=bool(data.is_active),
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate BOM code or header key (material / plant / alt / usage).")
        return BomRowOut(
            id=o.pk,
            code=o.code,
            name=o.name,
            parent_product_id=o.parent_product_id,
            warehouse_id=o.warehouse_id,
            usage=o.usage,
            alternative=int(o.alternative),
            valid_from=o.valid_from,
            valid_to=o.valid_to,
            is_active=o.is_active,
        )


class ProductBomLinesView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BomLineListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qd = getattr(self.request, "query", None) or {}
        bom_raw = (qd.get("bom_id") or "").strip()
        bom_id: int | None = None
        if bom_raw:
            try:
                bom_id = int(bom_raw)
            except ValueError:
                _bad("Invalid bom_id.")
        qs = fm.ProductBomLine.objects.select_related(
            "bom__parent_product", "component_product", "component_uom"
        ).order_by("bom__code", "position")
        if bom_id is not None:
            qs = qs.filter(bom_id=bom_id)
        if active_only:
            qs = qs.filter(bom__is_active=True)
        if q:
            qs = qs.filter(
                Q(bom__code__istartswith=q)
                | Q(component_product__code__istartswith=q)
                | Q(bom__parent_product__code__istartswith=q)
            )
        rows = await _slice_qs(qs, off, off + lim)
        return BomLineListOut(
            items=[
                BomLineRowOut(
                    id=o.pk,
                    bom_id=o.bom_id,
                    parent_product_id=o.bom.parent_product_id,
                    position=o.position,
                    component_product_id=o.component_product_id,
                    quantity=str(o.quantity),
                    component_uom_id=o.component_uom_id,
                    scrap_percent=str(o.scrap_percent),
                    item_text=o.item_text or "",
                    valid_from=o.valid_from,
                    valid_to=o.valid_to,
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: BomLineCreateIn) -> BomLineRowOut:
        _access(self.request)
        b = await fm.ProductBom.objects.filter(pk=data.bom_id).select_related("parent_product").afirst()
        if not b:
            _bad("Invalid bom_id.")
        if b.parent_product_id == data.component_product_id:
            _bad("Header material and component must differ.")
        if not await fm.Product.objects.filter(pk=data.component_product_id).aexists():
            _bad("Invalid component_product_id.")
        uomid = data.component_uom_id
        if uomid is not None and not await fm.UnitOfMeasure.objects.filter(pk=uomid).aexists():
            _bad("Invalid component_uom_id.")
        try:
            pos = max(1, int(data.position))
        except (TypeError, ValueError):
            _bad("Invalid position.")
        o = fm.ProductBomLine(
            bom_id=data.bom_id,
            position=pos,
            component_product_id=data.component_product_id,
            quantity=Decimal(str(data.quantity)),
            component_uom_id=uomid,
            scrap_percent=Decimal(str(data.scrap_percent or "0")),
            item_text=(data.item_text or "").strip(),
            valid_from=data.valid_from,
            valid_to=data.valid_to,
        )
        try:
            await o.asave()
        except IntegrityError:
            _bad("Duplicate BOM line position for this BOM.")
        return BomLineRowOut(
            id=o.pk,
            bom_id=o.bom_id,
            parent_product_id=b.parent_product_id,
            position=o.position,
            component_product_id=o.component_product_id,
            quantity=str(o.quantity),
            component_uom_id=o.component_uom_id,
            scrap_percent=str(o.scrap_percent),
            item_text=o.item_text or "",
            valid_from=o.valid_from,
            valid_to=o.valid_to,
        )


class WarehouseStocksView(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> StockListOut:
        _access(self.request)
        lim, off, q, active_only = _parse_query(self.request)
        qs = fm.WarehouseStock.objects.select_related("product", "warehouse").order_by("warehouse__code", "product__code")
        if q:
            qs = qs.filter(Q(product__code__istartswith=q) | Q(warehouse__code__istartswith=q))
        rows = await _slice_qs(qs, off, off + lim)
        return StockListOut(
            items=[
                StockRowOut(
                    id=o.pk,
                    product_id=o.product_id,
                    product_code=o.product.code,
                    warehouse_id=o.warehouse_id,
                    warehouse_code=o.warehouse.code,
                    quantity_on_hand=str(o.quantity_on_hand),
                )
                for o in rows
            ],
            limit=lim,
            offset=off,
        )

    async def post(self, data: StockCreateIn) -> StockRowOut:
        _access(self.request)
        if not await fm.Product.objects.filter(pk=data.product_id).aexists():
            _bad("Invalid product_id.")
        if not await fm.Warehouse.objects.filter(pk=data.warehouse_id).aexists():
            _bad("Invalid warehouse_id.")
        o, created = await fm.WarehouseStock.objects.aget_or_create(
            product_id=data.product_id,
            warehouse_id=data.warehouse_id,
            defaults={"quantity_on_hand": Decimal(str(data.quantity_on_hand or "0"))},
        )
        if not created:
            o.quantity_on_hand = Decimal(str(data.quantity_on_hand or "0"))
            await o.asave(update_fields=["quantity_on_hand", "updated_at"])
        p = await fm.Product.objects.aget(pk=o.product_id)
        w = await fm.Warehouse.objects.aget(pk=o.warehouse_id)
        return StockRowOut(
            id=o.pk,
            product_id=o.product_id,
            product_code=p.code,
            warehouse_id=o.warehouse_id,
            warehouse_code=w.code,
            quantity_on_hand=str(o.quantity_on_hand),
        )


def attach_foundation_routes(api: BoltAPI) -> None:
    tag = ["foundation"]
    api.view(_u("/currencies"), methods=["GET", "POST"], status_code=200, tags=tag)(CurrenciesView)
    api.view(_u("/tax-types"), methods=["GET", "POST"], status_code=200, tags=tag)(TaxTypesView)
    api.view(_u("/tax-rates"), methods=["GET", "POST"], status_code=200, tags=tag)(TaxRatesView)
    api.view(_u("/units-of-measure"), methods=["GET", "POST"], status_code=200, tags=tag)(UnitsOfMeasureView)
    api.view(_u("/categories"), methods=["GET", "POST"], status_code=200, tags=tag)(CategoriesView)
    api.view(_u("/warehouses"), methods=["GET", "POST"], status_code=200, tags=tag)(WarehousesView)
    api.view(_u("/payment-methods"), methods=["GET", "POST"], status_code=200, tags=tag)(PaymentMethodsView)
    api.view(_u("/payment-terms"), methods=["GET", "POST"], status_code=200, tags=tag)(PaymentTermsView)
    api.view(_u("/sales-persons"), methods=["GET", "POST"], status_code=200, tags=tag)(SalesPersonsView)
    api.view(_u("/suppliers"), methods=["GET", "POST"], status_code=200, tags=tag)(SuppliersView)
    api.view(_u("/customers"), methods=["GET", "POST"], status_code=200, tags=tag)(CustomersView)
    api.view(_u("/products"), methods=["GET", "POST"], status_code=200, tags=tag)(ProductsView)
    api.view(_u("/exchange-rates"), methods=["GET", "POST"], status_code=200, tags=tag)(ExchangeRatesView)
    api.view(_u("/uom-conversions"), methods=["GET", "POST"], status_code=200, tags=tag)(UomConversionsView)
    api.view(_u("/product-variants"), methods=["GET", "POST"], status_code=200, tags=tag)(ProductVariantsView)
    api.view(_u("/product-boms"), methods=["GET", "POST"], status_code=200, tags=tag)(ProductBomsView)
    api.view(_u("/product-bom-lines"), methods=["GET", "POST"], status_code=200, tags=tag)(ProductBomLinesView)
    api.view(_u("/warehouse-stocks"), methods=["GET", "POST"], status_code=200, tags=tag)(WarehouseStocksView)
