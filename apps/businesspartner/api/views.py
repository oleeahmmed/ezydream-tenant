"""
Business partner Bolt API — BP গ্রুপ, মাস্টার, ঠিকানা।

``django_bolt_guide.md``: ``APIView``, ``BadRequest`` / ``NotFound``। সিরিয়ালাইজার: ``serializers.py``।
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from urllib.parse import unquote

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.views import APIView

from apps.businesspartner.models import CRD1, OCRD, OCRG
from apps.warehouse.models import OWHS

from .serializers import (
    BPAddressCreateBody,
    BPAddressPage,
    BPAddressPatchBody,
    BPAddressResponse,
    BPGroupCreateBody,
    BPGroupPage,
    BPGroupPatchBody,
    BPGroupResponse,
    BusinessPartnerCreateBody,
    BusinessPartnerPage,
    BusinessPartnerPatchBody,
    BusinessPartnerResponse,
)


BUSINESSPARTNER_API_PREFIX = "/api/business-partners"


def _include_deleted(request: Any) -> bool:
    qd = getattr(request, "query", None) or {}
    return (qd.get("include_deleted") or "").strip().lower() in ("1", "true", "yes")


def _partner_response(o: OCRD) -> BusinessPartnerResponse:
    return BusinessPartnerResponse(
        CardCode=o.CardCode,
        CardName=o.CardName,
        CardType=o.CardType,
        GroupCode=o.GroupCode_id,
        CardFName=o.CardFName or "",
        CntctPrsn=o.CntctPrsn or "",
        Phone1=o.Phone1 or "",
        Phone2=o.Phone2 or "",
        Fax=o.Fax or "",
        Cellular=o.Cellular or "",
        E_Mail=o.E_Mail or "",
        Website=o.Website or "",
        LicTradNum=o.LicTradNum or "",
        CreditLine=str(o.CreditLine),
        DebtLine=str(o.DebtLine),
        Balance=str(o.Balance),
        OrdersBal=str(o.OrdersBal),
        DNotesBal=str(o.DNotesBal),
        Currency=o.Currency or "",
        PayTermsGrpCode=o.PayTermsGrpCode,
        DfltWhs=o.DfltWhs or "",
        ShipToDef=o.ShipToDef or "",
        BillToDef=o.BillToDef or "",
        SlpCode=o.SlpCode,
        Comments=o.Comments or "",
        ValidFor=o.ValidFor,
        Frozen=o.Frozen,
        Canceled=o.Canceled,
    )


def _address_response(o: CRD1) -> BPAddressResponse:
    return BPAddressResponse(
        CardCode=o.header_id,
        Address=o.Address,
        Street=o.Street or "",
        Block=o.Block or "",
        City=o.City or "",
        County=o.County or "",
        ZipCode=o.ZipCode or "",
        Country=o.Country or "",
        State=o.State or "",
        Building=o.Building or "",
        AdresType=o.AdresType,
        Canceled=o.Canceled,
    )


def _yn(value: str | None, field: str) -> str:
    if value is None:
        raise BadRequest(detail=f"{field} is required.")
    c = (value or "N").strip().upper()[:1] or "N"
    if c not in ("Y", "N"):
        raise BadRequest(detail=f"{field} must be Y or N.")
    return c


class BPGroupCollection(APIView):
    """BP groups (OCRG): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BPGroupPage:
        qd = getattr(self.request, "query", None) or {}
        try:
            limit = min(100, max(1, int(qd.get("limit", "50"))))
        except ValueError:
            limit = 50
        try:
            offset = max(0, int(qd.get("offset", "0")))
        except ValueError:
            offset = 0
        search_prefix = (qd.get("q") or "").strip()
        qs = OCRG.objects.all().order_by("GroupCode")
        if not _include_deleted(self.request):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            cond = Q(GroupName__istartswith=search_prefix)
            if search_prefix.isdigit():
                cond |= Q(GroupCode=int(search_prefix))
            qs = qs.filter(cond)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return BPGroupPage(
            items=[
                BPGroupResponse(GroupCode=o.GroupCode, GroupName=o.GroupName, GroupType=o.GroupType, Canceled=o.Canceled)
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: BPGroupCreateBody) -> BPGroupResponse:
        gt = (data.GroupType or "B").strip().upper()[:1] or "B"
        if gt not in ("C", "S", "B"):
            raise BadRequest(detail="GroupType must be C, S, or B.")
        o = OCRG(GroupCode=int(data.GroupCode), GroupName=data.GroupName.strip(), GroupType=gt)
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate GroupCode.")
        return BPGroupResponse(GroupCode=o.GroupCode, GroupName=o.GroupName, GroupType=o.GroupType, Canceled=o.Canceled)


class BPGroupDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, group_code: int) -> BPGroupResponse:
        try:
            o = await OCRG.objects.aget(pk=int(group_code))
        except OCRG.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return BPGroupResponse(GroupCode=o.GroupCode, GroupName=o.GroupName, GroupType=o.GroupType, Canceled=o.Canceled)

    async def patch(self, group_code: int, data: BPGroupPatchBody) -> BPGroupResponse:
        try:
            o = await OCRG.objects.aget(pk=int(group_code))
        except OCRG.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.GroupName is not None:
            o.GroupName = data.GroupName.strip()
        if data.GroupType is not None:
            gt = data.GroupType.strip().upper()[:1]
            if gt not in ("C", "S", "B"):
                raise BadRequest(detail="GroupType must be C, S, or B.")
            o.GroupType = gt
        if data.Canceled is not None:
            o.Canceled = _yn(data.Canceled, "Canceled")
        await o.asave()
        return BPGroupResponse(GroupCode=o.GroupCode, GroupName=o.GroupName, GroupType=o.GroupType, Canceled=o.Canceled)

    async def delete(self, group_code: int) -> BPGroupResponse:
        try:
            o = await OCRG.objects.aget(pk=int(group_code))
        except OCRG.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return BPGroupResponse(GroupCode=o.GroupCode, GroupName=o.GroupName, GroupType=o.GroupType, Canceled=o.Canceled)


class BusinessPartnerCollection(APIView):
    """Business partners (OCRD): list or create."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BusinessPartnerPage:
        qd = getattr(self.request, "query", None) or {}
        try:
            limit = min(100, max(1, int(qd.get("limit", "50"))))
        except ValueError:
            limit = 50
        try:
            offset = max(0, int(qd.get("offset", "0")))
        except ValueError:
            offset = 0
        search_prefix = (qd.get("q") or "").strip()
        qs = OCRD.objects.select_related("GroupCode").all().order_by("CardCode")
        if not _include_deleted(self.request):
            qs = qs.filter(Canceled="N")
        if search_prefix:
            qs = qs.filter(
                Q(CardCode__istartswith=search_prefix)
                | Q(CardName__istartswith=search_prefix)
                | Q(CntctPrsn__istartswith=search_prefix)
                | Q(E_Mail__istartswith=search_prefix)
                | Q(LicTradNum__istartswith=search_prefix)
            )
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return BusinessPartnerPage(items=[_partner_response(o) for o in rows], limit=limit, offset=offset)

    async def post(self, data: BusinessPartnerCreateBody) -> BusinessPartnerResponse:
        cc = data.CardCode.strip()
        if not cc:
            raise BadRequest(detail="CardCode is required.")
        ct = (data.CardType or "C").strip().upper()[:1] or "C"
        if ct not in ("C", "S", "L"):
            raise BadRequest(detail="CardType must be C, S, or L.")
        gc_id = data.GroupCode
        if gc_id is not None and not await OCRG.objects.filter(pk=int(gc_id)).aexists():
            raise BadRequest(detail="Invalid GroupCode (OCRG).")
        dw = (data.DfltWhs or "").strip()[:20]
        if dw and not await OWHS.objects.filter(WhsCode=dw, Inactive="N").aexists():
            raise BadRequest(detail="Default warehouse not found or inactive (OWHS).")
        o = OCRD(
            CardCode=cc,
            CardName=data.CardName.strip(),
            CardType=ct,
            GroupCode_id=int(gc_id) if gc_id is not None else None,
            CardFName=(data.CardFName or "").strip()[:200],
            CntctPrsn=(data.CntctPrsn or "").strip()[:100],
            Phone1=(data.Phone1 or "").strip()[:50],
            Phone2=(data.Phone2 or "").strip()[:50],
            Fax=(data.Fax or "").strip()[:50],
            Cellular=(data.Cellular or "").strip()[:50],
            E_Mail=(data.E_Mail or "").strip()[:100],
            Website=(data.Website or "").strip()[:100],
            LicTradNum=(data.LicTradNum or "").strip()[:32],
            CreditLine=Decimal(str(data.CreditLine or "0")),
            DebtLine=Decimal(str(data.DebtLine or "0")),
            Balance=Decimal(str(data.Balance or "0")),
            OrdersBal=Decimal(str(data.OrdersBal or "0")),
            DNotesBal=Decimal(str(data.DNotesBal or "0")),
            Currency=(data.Currency or "").strip()[:15],
            PayTermsGrpCode=data.PayTermsGrpCode,
            DfltWhs=dw,
            ShipToDef=(data.ShipToDef or "").strip()[:50],
            BillToDef=(data.BillToDef or "").strip()[:50],
            SlpCode=data.SlpCode,
            Comments=(data.Comments or "").strip(),
            ValidFor=_yn(data.ValidFor, "ValidFor"),
            Frozen=_yn(data.Frozen, "Frozen"),
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate CardCode.")
        return _partner_response(o)


class BusinessPartnerDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, card_code: str) -> BusinessPartnerResponse:
        pk = card_code.strip()
        try:
            o = await OCRD.objects.select_related("GroupCode").aget(pk=pk)
        except OCRD.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return _partner_response(o)

    async def patch(self, card_code: str, data: BusinessPartnerPatchBody) -> BusinessPartnerResponse:
        pk = card_code.strip()
        try:
            o = await OCRD.objects.select_related("GroupCode").aget(pk=pk)
        except OCRD.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.CardName is not None:
            o.CardName = data.CardName.strip()
        if data.CardType is not None:
            ct = data.CardType.strip().upper()[:1]
            if ct not in ("C", "S", "L"):
                raise BadRequest(detail="CardType must be C, S, or L.")
            o.CardType = ct
        if data.GroupCode is not None:
            if not await OCRG.objects.filter(pk=int(data.GroupCode)).aexists():
                raise BadRequest(detail="Invalid GroupCode (OCRG).")
            o.GroupCode_id = int(data.GroupCode)
        if data.CardFName is not None:
            o.CardFName = data.CardFName.strip()[:200]
        if data.CntctPrsn is not None:
            o.CntctPrsn = data.CntctPrsn.strip()[:100]
        if data.Phone1 is not None:
            o.Phone1 = data.Phone1.strip()[:50]
        if data.Phone2 is not None:
            o.Phone2 = data.Phone2.strip()[:50]
        if data.Fax is not None:
            o.Fax = data.Fax.strip()[:50]
        if data.Cellular is not None:
            o.Cellular = data.Cellular.strip()[:50]
        if data.E_Mail is not None:
            o.E_Mail = data.E_Mail.strip()[:100]
        if data.Website is not None:
            o.Website = data.Website.strip()[:100]
        if data.LicTradNum is not None:
            o.LicTradNum = data.LicTradNum.strip()[:32]
        if data.CreditLine is not None:
            o.CreditLine = Decimal(str(data.CreditLine))
        if data.DebtLine is not None:
            o.DebtLine = Decimal(str(data.DebtLine))
        if data.Balance is not None:
            o.Balance = Decimal(str(data.Balance))
        if data.OrdersBal is not None:
            o.OrdersBal = Decimal(str(data.OrdersBal))
        if data.DNotesBal is not None:
            o.DNotesBal = Decimal(str(data.DNotesBal))
        if data.Currency is not None:
            o.Currency = data.Currency.strip()[:15]
        if data.PayTermsGrpCode is not None:
            o.PayTermsGrpCode = data.PayTermsGrpCode
        if data.DfltWhs is not None:
            dw = data.DfltWhs.strip()[:20]
            if dw and not await OWHS.objects.filter(WhsCode=dw, Inactive="N").aexists():
                raise BadRequest(detail="Default warehouse not found or inactive (OWHS).")
            o.DfltWhs = dw
        if data.ShipToDef is not None:
            o.ShipToDef = data.ShipToDef.strip()[:50]
        if data.BillToDef is not None:
            o.BillToDef = data.BillToDef.strip()[:50]
        if data.SlpCode is not None:
            o.SlpCode = data.SlpCode
        if data.Comments is not None:
            o.Comments = data.Comments.strip()
        if data.ValidFor is not None:
            o.ValidFor = _yn(data.ValidFor, "ValidFor")
        if data.Frozen is not None:
            o.Frozen = _yn(data.Frozen, "Frozen")
        if data.Canceled is not None:
            o.Canceled = _yn(data.Canceled, "Canceled")
        await o.asave()
        return _partner_response(o)

    async def delete(self, card_code: str) -> BusinessPartnerResponse:
        pk = card_code.strip()
        try:
            o = await OCRD.objects.select_related("GroupCode").aget(pk=pk)
        except OCRD.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return _partner_response(o)


class BPAddressCollection(APIView):
    """BP addresses (CRD1) for one CardCode."""

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, card_code: str) -> BPAddressPage:
        pk = card_code.strip()
        if not await OCRD.objects.filter(pk=pk).aexists():
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        qd = getattr(self.request, "query", None) or {}
        try:
            limit = min(100, max(1, int(qd.get("limit", "50"))))
        except ValueError:
            limit = 50
        try:
            offset = max(0, int(qd.get("offset", "0")))
        except ValueError:
            offset = 0
        qs = CRD1.objects.filter(header_id=pk).order_by("Address")
        if not _include_deleted(self.request):
            qs = qs.filter(Canceled="N")
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return BPAddressPage(items=[_address_response(o) for o in rows], limit=limit, offset=offset)

    async def post(self, card_code: str, data: BPAddressCreateBody) -> BPAddressResponse:
        pk = card_code.strip()
        try:
            header = await OCRD.objects.aget(pk=pk)
        except OCRD.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and header.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        addr = data.Address.strip()
        if not addr:
            raise BadRequest(detail="Address is required.")
        at = (data.AdresType or "S").strip().upper()[:1] or "S"
        if at not in ("B", "S"):
            raise BadRequest(detail="AdresType must be B or S.")
        o = CRD1(
            header=header,
            Address=addr[:50],
            Street=(data.Street or "").strip()[:100],
            Block=(data.Block or "").strip()[:100],
            City=(data.City or "").strip()[:100],
            County=(data.County or "").strip()[:100],
            ZipCode=(data.ZipCode or "").strip()[:20],
            Country=(data.Country or "").strip()[:3],
            State=(data.State or "").strip()[:3],
            Building=(data.Building or "").strip()[:100],
            AdresType=at,
            Canceled=_yn(data.Canceled, "Canceled"),
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate Address for this CardCode.")
        return _address_response(o)


class BPAddressDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, card_code: str, address: str) -> BPAddressResponse:
        pk = card_code.strip()
        aid = unquote(address).strip()
        try:
            o = await CRD1.objects.select_related("header").aget(header_id=pk, Address=aid)
        except CRD1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return _address_response(o)

    async def patch(self, card_code: str, address: str, data: BPAddressPatchBody) -> BPAddressResponse:
        pk = card_code.strip()
        aid = unquote(address).strip()
        try:
            o = await CRD1.objects.select_related("header").aget(header_id=pk, Address=aid)
        except CRD1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.Street is not None:
            o.Street = data.Street.strip()[:100]
        if data.Block is not None:
            o.Block = data.Block.strip()[:100]
        if data.City is not None:
            o.City = data.City.strip()[:100]
        if data.County is not None:
            o.County = data.County.strip()[:100]
        if data.ZipCode is not None:
            o.ZipCode = data.ZipCode.strip()[:20]
        if data.Country is not None:
            o.Country = data.Country.strip()[:3]
        if data.State is not None:
            o.State = data.State.strip()[:3]
        if data.Building is not None:
            o.Building = data.Building.strip()[:100]
        if data.AdresType is not None:
            at = data.AdresType.strip().upper()[:1]
            if at not in ("B", "S"):
                raise BadRequest(detail="AdresType must be B or S.")
            o.AdresType = at
        if data.Canceled is not None:
            o.Canceled = _yn(data.Canceled, "Canceled")
        await o.asave()
        return _address_response(o)

    async def delete(self, card_code: str, address: str) -> BPAddressResponse:
        pk = card_code.strip()
        aid = unquote(address).strip()
        try:
            o = await CRD1.objects.select_related("header").aget(header_id=pk, Address=aid)
        except CRD1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if not _include_deleted(self.request) and o.Canceled == "Y":
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        o.Canceled = "Y"
        await o.asave(update_fields=["Canceled"])
        return _address_response(o)


def attach_businesspartner_routes(api: BoltAPI) -> None:
    """Register all business-partner Bolt routes on the given API object."""

    tag = ["business-partners"]
    p = BUSINESSPARTNER_API_PREFIX
    # Literal ``groups`` / ``ocrg`` before ``{card_code}`` to avoid shadowing.
    api.view(p + "/groups", methods=["GET", "POST"], status_code=200, tags=tag)(BPGroupCollection)
    api.view(p + "/groups/{group_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(BPGroupDetail)
    api.view(p + "/ocrg", methods=["GET", "POST"], status_code=200, tags=tag)(BPGroupCollection)
    api.view(p + "/ocrg/{group_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(BPGroupDetail)
    api.view(p, methods=["GET", "POST"], status_code=200, tags=tag)(BusinessPartnerCollection)
    api.view(p + "/ocrd", methods=["GET", "POST"], status_code=200, tags=tag)(BusinessPartnerCollection)
    api.view(p + "/{card_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(BusinessPartnerDetail)
    api.view(p + "/ocrd/{card_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(BusinessPartnerDetail)
    api.view(p + "/{card_code}/addresses", methods=["GET", "POST"], status_code=200, tags=tag)(BPAddressCollection)
    api.view(p + "/ocrd/{card_code}/addresses", methods=["GET", "POST"], status_code=200, tags=tag)(BPAddressCollection)
    api.view(
        p + "/{card_code}/addresses/{address}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(BPAddressDetail)
    api.view(
        p + "/ocrd/{card_code}/addresses/{address}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(BPAddressDetail)
