
"""
Finance Bolt API — GL, জার্নাল, ব্যাংকিং, ট্যাক্স, পিরিয়ড, বাজেট।

``django_bolt_guide.md``: ``APIView``, ``BadRequest`` / ``NotFound``। সিরিয়ালাইজার: ``serializers.py``।
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from asgiref.sync import sync_to_async
from django.db import IntegrityError
from django.db.models import Q
from django_bolt import BoltAPI
from django_bolt.auth import IsAuthenticated, JWTAuthentication
from django_bolt.exceptions import BadRequest, NotFound
from django_bolt.views import APIView

from apps.finance.models import BGT1, JDT1, OACT, OBGT, OJDT, OFPR, OPRC, ORCT, OSTC, OVPM, RCT1, VPM1

from .serializers import (
    BudgetLineCreateBody,
    BudgetLinePage,
    BudgetLinePatchBody,
    BudgetLineResponse,
    BudgetSetupCreateBody,
    BudgetSetupPage,
    BudgetSetupPatchBody,
    BudgetSetupResponse,
    FinancialPeriodCreateBody,
    FinancialPeriodPage,
    FinancialPeriodPatchBody,
    FinancialPeriodResponse,
    GlAccountCreateBody,
    GlAccountPage,
    GlAccountPatchBody,
    GlAccountResponse,
    IncomingPaymentCreateBody,
    IncomingPaymentLineCreateBody,
    IncomingPaymentLinePage,
    IncomingPaymentLinePatchBody,
    IncomingPaymentLineResponse,
    IncomingPaymentPage,
    IncomingPaymentPatchBody,
    IncomingPaymentResponse,
    JournalEntryCreateBody,
    JournalEntryLineCreateBody,
    JournalEntryLinePage,
    JournalEntryLinePatchBody,
    JournalEntryLineResponse,
    JournalEntryPage,
    JournalEntryPatchBody,
    JournalEntryResponse,
    OutgoingPaymentCreateBody,
    OutgoingPaymentLineCreateBody,
    OutgoingPaymentLinePage,
    OutgoingPaymentLinePatchBody,
    OutgoingPaymentLineResponse,
    OutgoingPaymentPage,
    OutgoingPaymentPatchBody,
    OutgoingPaymentResponse,
    ProfitCenterCreateBody,
    ProfitCenterPage,
    ProfitCenterPatchBody,
    ProfitCenterResponse,
    TaxCodeCreateBody,
    TaxCodePage,
    TaxCodePatchBody,
    TaxCodeResponse,
)


FINANCE_API_PREFIX = "/api/finance"


def _read_pagination(request: Any) -> tuple[int, int, str]:
    qd = getattr(request, "query", None) or {}
    try:
        limit = min(100, max(1, int(qd.get("limit", "50"))))
    except ValueError:
        limit = 50
    try:
        offset = max(0, int(qd.get("offset", "0")))
    except ValueError:
        offset = 0
    search_prefix = (qd.get("q") or "").strip()
    return limit, offset, search_prefix


def _yn(name: str, v: str | None) -> str:
    if v is None:
        raise BadRequest(detail=f"{name} required.")
    c = (v or "N").strip().upper()[:1] or "N"
    if c not in ("Y", "N"):
        raise BadRequest(detail=f"{name} must be Y or N.")
    return c

class GlAccountCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> GlAccountPage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = OACT.objects.all().order_by("AcctCode")
        if search_prefix:
            qs = qs.filter(Q(AcctCode__istartswith=search_prefix) | Q(AcctName__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return GlAccountPage(
            items=[
                GlAccountResponse(
                    AcctCode=o.AcctCode,
                    AcctName=o.AcctName,
                    CurrTotal=str(o.CurrTotal),
                    GroupMask=o.GroupMask,
                    FatherNum=o.FatherNum or "",
                    Postable=o.Postable,
                    LocCash=o.LocCash,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: GlAccountCreateBody) -> GlAccountResponse:
        if int(data.GroupMask) not in (1, 2, 3, 4, 5):
            raise BadRequest(detail="GroupMask must be 1–5.")
        postable = _yn("Postable", data.Postable)
        loccash = _yn("LocCash", data.LocCash)
        o = OACT(
            AcctCode=data.AcctCode.strip(),
            AcctName=data.AcctName.strip(),
            CurrTotal=Decimal(str(data.CurrTotal or "0")),
            GroupMask=int(data.GroupMask),
            FatherNum=(data.FatherNum or "").strip(),
            Postable=postable,
            LocCash=loccash,
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate AcctCode or invalid data.")
        return GlAccountResponse(
            AcctCode=o.AcctCode,
            AcctName=o.AcctName,
            CurrTotal=str(o.CurrTotal),
            GroupMask=o.GroupMask,
            FatherNum=o.FatherNum or "",
            Postable=o.Postable,
            LocCash=o.LocCash,
        )


class GlAccountDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, acct_code: str) -> GlAccountResponse:
        try:
            o = await OACT.objects.aget(pk=acct_code.strip())
        except OACT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return GlAccountResponse(
            AcctCode=o.AcctCode,
            AcctName=o.AcctName,
            CurrTotal=str(o.CurrTotal),
            GroupMask=o.GroupMask,
            FatherNum=o.FatherNum or "",
            Postable=o.Postable,
            LocCash=o.LocCash,
        )

    async def patch(self, acct_code: str, data: GlAccountPatchBody) -> GlAccountResponse:
        try:
            o = await OACT.objects.aget(pk=acct_code.strip())
        except OACT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.AcctName is not None:
            o.AcctName = data.AcctName.strip()
        if data.CurrTotal is not None:
            o.CurrTotal = Decimal(str(data.CurrTotal))
        if data.GroupMask is not None:
            if int(data.GroupMask) not in (1, 2, 3, 4, 5):
                raise BadRequest(detail="GroupMask must be 1–5.")
            o.GroupMask = int(data.GroupMask)
        if data.FatherNum is not None:
            o.FatherNum = data.FatherNum.strip()
        if data.Postable is not None:
            o.Postable = _yn("Postable", data.Postable)
        if data.LocCash is not None:
            o.LocCash = _yn("LocCash", data.LocCash)
        await o.asave()
        return GlAccountResponse(
            AcctCode=o.AcctCode,
            AcctName=o.AcctName,
            CurrTotal=str(o.CurrTotal),
            GroupMask=o.GroupMask,
            FatherNum=o.FatherNum or "",
            Postable=o.Postable,
            LocCash=o.LocCash,
        )

    async def delete(self, acct_code: str) -> GlAccountResponse:
        try:
            o = await OACT.objects.aget(pk=acct_code.strip())
        except OACT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = GlAccountResponse(
            AcctCode=o.AcctCode,
            AcctName=o.AcctName,
            CurrTotal=str(o.CurrTotal),
            GroupMask=o.GroupMask,
            FatherNum=o.FatherNum or "",
            Postable=o.Postable,
            LocCash=o.LocCash,
        )
        await o.adelete()
        return rep

class ProfitCenterCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> ProfitCenterPage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = OPRC.objects.all().order_by("PrcCode")
        if search_prefix:
            qs = qs.filter(Q(PrcCode__istartswith=search_prefix) | Q(PrcName__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return ProfitCenterPage(
            items=[
                ProfitCenterResponse(
                    PrcCode=o.PrcCode,
                    PrcName=o.PrcName,
                    DimCode=o.DimCode,
                    Active=o.Active,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: ProfitCenterCreateBody) -> ProfitCenterResponse:
        if int(data.DimCode) not in (1, 2, 3, 4, 5):
            raise BadRequest(detail="DimCode must be 1–5.")
        active = _yn("Active", data.Active)
        o = OPRC(
            PrcCode=data.PrcCode.strip(),
            PrcName=data.PrcName.strip(),
            DimCode=int(data.DimCode),
            Active=active,
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate PrcCode.")
        return ProfitCenterResponse(PrcCode=o.PrcCode, PrcName=o.PrcName, DimCode=o.DimCode, Active=o.Active)


class ProfitCenterDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, prc_code: str) -> ProfitCenterResponse:
        try:
            o = await OPRC.objects.aget(pk=prc_code.strip())
        except OPRC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return ProfitCenterResponse(PrcCode=o.PrcCode, PrcName=o.PrcName, DimCode=o.DimCode, Active=o.Active)

    async def patch(self, prc_code: str, data: ProfitCenterPatchBody) -> ProfitCenterResponse:
        try:
            o = await OPRC.objects.aget(pk=prc_code.strip())
        except OPRC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.PrcName is not None:
            o.PrcName = data.PrcName.strip()
        if data.DimCode is not None:
            if int(data.DimCode) not in (1, 2, 3, 4, 5):
                raise BadRequest(detail="DimCode must be 1–5.")
            o.DimCode = int(data.DimCode)
        if data.Active is not None:
            o.Active = _yn("Active", data.Active)
        await o.asave()
        return ProfitCenterResponse(PrcCode=o.PrcCode, PrcName=o.PrcName, DimCode=o.DimCode, Active=o.Active)

    async def delete(self, prc_code: str) -> ProfitCenterResponse:
        try:
            o = await OPRC.objects.aget(pk=prc_code.strip())
        except OPRC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = ProfitCenterResponse(PrcCode=o.PrcCode, PrcName=o.PrcName, DimCode=o.DimCode, Active=o.Active)
        await o.adelete()
        return rep

class JournalEntryCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> JournalEntryPage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = OJDT.objects.all().order_by("-TransId")
        if search_prefix:
            qs = qs.filter(BaseRef__istartswith=search_prefix)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return JournalEntryPage(
            items=[
                JournalEntryResponse(
                    TransId=o.TransId,
                    BaseRef=o.BaseRef or "",
                    RefDate=o.RefDate,
                    TransType=o.TransType,
                    Memo=o.Memo or "",
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: JournalEntryCreateBody) -> JournalEntryResponse:
        o = OJDT(
            BaseRef=(data.BaseRef or "").strip(),
            RefDate=data.RefDate,
            TransType=int(data.TransType),
            Memo=(data.Memo or "").strip(),
        )
        await o.asave()
        return JournalEntryResponse(
            TransId=o.TransId,
            BaseRef=o.BaseRef or "",
            RefDate=o.RefDate,
            TransType=o.TransType,
            Memo=o.Memo or "",
        )


class JournalEntryDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, trans_id: int) -> JournalEntryResponse:
        try:
            o = await OJDT.objects.aget(pk=trans_id)
        except OJDT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return JournalEntryResponse(
            TransId=o.TransId,
            BaseRef=o.BaseRef or "",
            RefDate=o.RefDate,
            TransType=o.TransType,
            Memo=o.Memo or "",
        )

    async def patch(self, trans_id: int, data: JournalEntryPatchBody) -> JournalEntryResponse:
        try:
            o = await OJDT.objects.aget(pk=trans_id)
        except OJDT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.BaseRef is not None:
            o.BaseRef = data.BaseRef.strip()
        if data.RefDate is not None:
            o.RefDate = data.RefDate
        if data.TransType is not None:
            o.TransType = int(data.TransType)
        if data.Memo is not None:
            o.Memo = data.Memo.strip()
        await o.asave()
        return JournalEntryResponse(
            TransId=o.TransId,
            BaseRef=o.BaseRef or "",
            RefDate=o.RefDate,
            TransType=o.TransType,
            Memo=o.Memo or "",
        )

    async def delete(self, trans_id: int) -> JournalEntryResponse:
        try:
            o = await OJDT.objects.aget(pk=trans_id)
        except OJDT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = JournalEntryResponse(
            TransId=o.TransId,
            BaseRef=o.BaseRef or "",
            RefDate=o.RefDate,
            TransType=o.TransType,
            Memo=o.Memo or "",
        )
        await o.adelete()
        return rep


class JournalEntryLineCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> JournalEntryLinePage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qd = getattr(self.request, "query", None) or {}
        raw = (qd.get("trans_id") or "").strip()
        trans_id = int(raw) if raw else None
        qs = JDT1.objects.all().order_by("header_id", "Line_ID")
        if trans_id is not None:
            qs = qs.filter(header_id=trans_id)
        if search_prefix:
            qs = qs.filter(Q(Account__istartswith=search_prefix) | Q(ShortName__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return JournalEntryLinePage(
            items=[
                JournalEntryLineResponse(
                    TransId=o.header_id,
                    Line_ID=o.Line_ID,
                    Account=o.Account,
                    ShortName=o.ShortName or "",
                    Debit=str(o.Debit),
                    Credit=str(o.Credit),
                    ProfitCode=o.ProfitCode or "",
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: JournalEntryLineCreateBody) -> JournalEntryLineResponse:
        if not await OJDT.objects.filter(pk=data.TransId).aexists():
            raise BadRequest(detail="Invalid TransId (OJDT).")
        line = JDT1(
            header_id=data.TransId,
            Line_ID=int(data.Line_ID),
            Account=data.Account.strip(),
            ShortName=(data.ShortName or "").strip(),
            Debit=Decimal(str(data.Debit or "0")),
            Credit=Decimal(str(data.Credit or "0")),
            ProfitCode=(data.ProfitCode or "").strip(),
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid TransId.")
        return JournalEntryLineResponse(
            TransId=line.header_id,
            Line_ID=line.Line_ID,
            Account=line.Account,
            ShortName=line.ShortName or "",
            Debit=str(line.Debit),
            Credit=str(line.Credit),
            ProfitCode=line.ProfitCode or "",
        )


class JournalEntryLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, trans_id: int, line_id: int) -> JournalEntryLineResponse:
        try:
            o = await JDT1.objects.select_related("header").aget(header_id=trans_id, Line_ID=int(line_id))
        except JDT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return JournalEntryLineResponse(
            TransId=o.header_id,
            Line_ID=o.Line_ID,
            Account=o.Account,
            ShortName=o.ShortName or "",
            Debit=str(o.Debit),
            Credit=str(o.Credit),
            ProfitCode=o.ProfitCode or "",
        )

    async def patch(self, trans_id: int, line_id: int, data: JournalEntryLinePatchBody) -> JournalEntryLineResponse:
        try:
            o = await JDT1.objects.select_related("header").aget(header_id=trans_id, Line_ID=int(line_id))
        except JDT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.Account is not None:
            o.Account = data.Account.strip()
        if data.ShortName is not None:
            o.ShortName = data.ShortName.strip()
        if data.Debit is not None:
            o.Debit = Decimal(str(data.Debit))
        if data.Credit is not None:
            o.Credit = Decimal(str(data.Credit))
        if data.ProfitCode is not None:
            o.ProfitCode = data.ProfitCode.strip()
        await o.asave()
        return JournalEntryLineResponse(
            TransId=o.header_id,
            Line_ID=o.Line_ID,
            Account=o.Account,
            ShortName=o.ShortName or "",
            Debit=str(o.Debit),
            Credit=str(o.Credit),
            ProfitCode=o.ProfitCode or "",
        )

    async def delete(self, trans_id: int, line_id: int) -> JournalEntryLineResponse:
        try:
            o = await JDT1.objects.select_related("header").aget(header_id=trans_id, Line_ID=int(line_id))
        except JDT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = JournalEntryLineResponse(
            TransId=o.header_id,
            Line_ID=o.Line_ID,
            Account=o.Account,
            ShortName=o.ShortName or "",
            Debit=str(o.Debit),
            Credit=str(o.Credit),
            ProfitCode=o.ProfitCode or "",
        )
        await o.adelete()
        return rep

class IncomingPaymentCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> IncomingPaymentPage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = ORCT.objects.all().order_by("-DocEntry")
        if search_prefix:
            qs = qs.filter(Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return IncomingPaymentPage(
            items=[
                IncomingPaymentResponse(
                    DocEntry=o.DocEntry,
                    CardCode=o.CardCode,
                    CardName=o.CardName or "",
                    DocDate=o.DocDate,
                    CashAcct=o.CashAcct or "",
                    CheckAcct=o.CheckAcct or "",
                    DocTotal=str(o.DocTotal),
                    CashSum=str(o.CashSum),
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: IncomingPaymentCreateBody) -> IncomingPaymentResponse:
        o = ORCT(
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocDate=data.DocDate,
            CashAcct=(data.CashAcct or "").strip(),
            CheckAcct=(data.CheckAcct or "").strip(),
            DocTotal=Decimal(str(data.DocTotal or "0")),
            CashSum=Decimal(str(data.CashSum or "0")),
        )
        await o.asave()
        return IncomingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            CashAcct=o.CashAcct or "",
            CheckAcct=o.CheckAcct or "",
            DocTotal=str(o.DocTotal),
            CashSum=str(o.CashSum),
        )


class IncomingPaymentDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> IncomingPaymentResponse:
        try:
            o = await ORCT.objects.aget(pk=doc_entry)
        except ORCT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return IncomingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            CashAcct=o.CashAcct or "",
            CheckAcct=o.CheckAcct or "",
            DocTotal=str(o.DocTotal),
            CashSum=str(o.CashSum),
        )

    async def patch(self, doc_entry: int, data: IncomingPaymentPatchBody) -> IncomingPaymentResponse:
        try:
            o = await ORCT.objects.aget(pk=doc_entry)
        except ORCT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.CardCode is not None:
            o.CardCode = data.CardCode.strip()
        if data.CardName is not None:
            o.CardName = data.CardName.strip()
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.CashAcct is not None:
            o.CashAcct = data.CashAcct.strip()
        if data.CheckAcct is not None:
            o.CheckAcct = data.CheckAcct.strip()
        if data.DocTotal is not None:
            o.DocTotal = Decimal(str(data.DocTotal))
        if data.CashSum is not None:
            o.CashSum = Decimal(str(data.CashSum))
        await o.asave()
        return IncomingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            CashAcct=o.CashAcct or "",
            CheckAcct=o.CheckAcct or "",
            DocTotal=str(o.DocTotal),
            CashSum=str(o.CashSum),
        )

    async def delete(self, doc_entry: int) -> IncomingPaymentResponse:
        try:
            o = await ORCT.objects.aget(pk=doc_entry)
        except ORCT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = IncomingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            CashAcct=o.CashAcct or "",
            CheckAcct=o.CheckAcct or "",
            DocTotal=str(o.DocTotal),
            CashSum=str(o.CashSum),
        )
        await o.adelete()
        return rep


class IncomingPaymentLineCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> IncomingPaymentLinePage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qd = getattr(self.request, "query", None) or {}
        raw = (qd.get("doc_entry") or "").strip()
        doc_entry = int(raw) if raw else None
        qs = RCT1.objects.all().order_by("header_id", "LineNum")
        if doc_entry is not None:
            qs = qs.filter(header_id=doc_entry)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return IncomingPaymentLinePage(
            items=[
                IncomingPaymentLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    DocNum=o.DocNum,
                    SumApplied=str(o.SumApplied),
                    InvType=o.InvType,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: IncomingPaymentLineCreateBody) -> IncomingPaymentLineResponse:
        if not await ORCT.objects.filter(pk=data.DocEntry).aexists():
            raise BadRequest(detail="Invalid DocEntry (ORCT).")
        line = RCT1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            DocNum=data.DocNum,
            SumApplied=Decimal(str(data.SumApplied)),
            InvType=int(data.InvType),
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return IncomingPaymentLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            DocNum=line.DocNum,
            SumApplied=str(line.SumApplied),
            InvType=line.InvType,
        )


class IncomingPaymentLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> IncomingPaymentLineResponse:
        try:
            o = await RCT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RCT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return IncomingPaymentLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            DocNum=o.DocNum,
            SumApplied=str(o.SumApplied),
            InvType=o.InvType,
        )

    async def patch(self, doc_entry: int, line_num: int, data: IncomingPaymentLinePatchBody) -> IncomingPaymentLineResponse:
        try:
            o = await RCT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RCT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.SumApplied is not None:
            o.SumApplied = Decimal(str(data.SumApplied))
        if data.InvType is not None:
            o.InvType = int(data.InvType)
        await o.asave()
        return IncomingPaymentLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            DocNum=o.DocNum,
            SumApplied=str(o.SumApplied),
            InvType=o.InvType,
        )

    async def delete(self, doc_entry: int, line_num: int) -> IncomingPaymentLineResponse:
        try:
            o = await RCT1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except RCT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = IncomingPaymentLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            DocNum=o.DocNum,
            SumApplied=str(o.SumApplied),
            InvType=o.InvType,
        )
        await o.adelete()
        return rep


class OutgoingPaymentCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> OutgoingPaymentPage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = OVPM.objects.all().order_by("-DocEntry")
        if search_prefix:
            qs = qs.filter(Q(CardCode__istartswith=search_prefix) | Q(CardName__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return OutgoingPaymentPage(
            items=[
                OutgoingPaymentResponse(
                    DocEntry=o.DocEntry,
                    CardCode=o.CardCode,
                    CardName=o.CardName or "",
                    DocDate=o.DocDate,
                    BankAcct=o.BankAcct or "",
                    CashSum=str(o.CashSum),
                    TrsfrSum=str(o.TrsfrSum),
                    DocTotal=str(o.DocTotal),
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: OutgoingPaymentCreateBody) -> OutgoingPaymentResponse:
        o = OVPM(
            CardCode=data.CardCode.strip(),
            CardName=(data.CardName or "").strip(),
            DocDate=data.DocDate,
            BankAcct=(data.BankAcct or "").strip(),
            CashSum=Decimal(str(data.CashSum or "0")),
            TrsfrSum=Decimal(str(data.TrsfrSum or "0")),
            DocTotal=Decimal(str(data.DocTotal or "0")),
        )
        await o.asave()
        return OutgoingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            BankAcct=o.BankAcct or "",
            CashSum=str(o.CashSum),
            TrsfrSum=str(o.TrsfrSum),
            DocTotal=str(o.DocTotal),
        )


class OutgoingPaymentDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int) -> OutgoingPaymentResponse:
        try:
            o = await OVPM.objects.aget(pk=doc_entry)
        except OVPM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return OutgoingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            BankAcct=o.BankAcct or "",
            CashSum=str(o.CashSum),
            TrsfrSum=str(o.TrsfrSum),
            DocTotal=str(o.DocTotal),
        )

    async def patch(self, doc_entry: int, data: OutgoingPaymentPatchBody) -> OutgoingPaymentResponse:
        try:
            o = await OVPM.objects.aget(pk=doc_entry)
        except OVPM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.CardCode is not None:
            o.CardCode = data.CardCode.strip()
        if data.CardName is not None:
            o.CardName = data.CardName.strip()
        if data.DocDate is not None:
            o.DocDate = data.DocDate
        if data.BankAcct is not None:
            o.BankAcct = data.BankAcct.strip()
        if data.CashSum is not None:
            o.CashSum = Decimal(str(data.CashSum))
        if data.TrsfrSum is not None:
            o.TrsfrSum = Decimal(str(data.TrsfrSum))
        if data.DocTotal is not None:
            o.DocTotal = Decimal(str(data.DocTotal))
        await o.asave()
        return OutgoingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            BankAcct=o.BankAcct or "",
            CashSum=str(o.CashSum),
            TrsfrSum=str(o.TrsfrSum),
            DocTotal=str(o.DocTotal),
        )

    async def delete(self, doc_entry: int) -> OutgoingPaymentResponse:
        try:
            o = await OVPM.objects.aget(pk=doc_entry)
        except OVPM.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = OutgoingPaymentResponse(
            DocEntry=o.DocEntry,
            CardCode=o.CardCode,
            CardName=o.CardName or "",
            DocDate=o.DocDate,
            BankAcct=o.BankAcct or "",
            CashSum=str(o.CashSum),
            TrsfrSum=str(o.TrsfrSum),
            DocTotal=str(o.DocTotal),
        )
        await o.adelete()
        return rep


class OutgoingPaymentLineCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> OutgoingPaymentLinePage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qd = getattr(self.request, "query", None) or {}
        raw = (qd.get("doc_entry") or "").strip()
        doc_entry = int(raw) if raw else None
        qs = VPM1.objects.all().order_by("header_id", "LineNum")
        if doc_entry is not None:
            qs = qs.filter(header_id=doc_entry)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return OutgoingPaymentLinePage(
            items=[
                OutgoingPaymentLineResponse(
                    DocEntry=o.header_id,
                    LineNum=o.LineNum,
                    DocNum=o.DocNum,
                    SumApplied=str(o.SumApplied),
                    InvType=o.InvType,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: OutgoingPaymentLineCreateBody) -> OutgoingPaymentLineResponse:
        if not await OVPM.objects.filter(pk=data.DocEntry).aexists():
            raise BadRequest(detail="Invalid DocEntry (OVPM).")
        line = VPM1(
            header_id=data.DocEntry,
            LineNum=int(data.LineNum),
            DocNum=data.DocNum,
            SumApplied=Decimal(str(data.SumApplied)),
            InvType=int(data.InvType),
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate line or invalid DocEntry.")
        return OutgoingPaymentLineResponse(
            DocEntry=line.header_id,
            LineNum=line.LineNum,
            DocNum=line.DocNum,
            SumApplied=str(line.SumApplied),
            InvType=line.InvType,
        )


class OutgoingPaymentLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, doc_entry: int, line_num: int) -> OutgoingPaymentLineResponse:
        try:
            o = await VPM1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except VPM1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return OutgoingPaymentLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            DocNum=o.DocNum,
            SumApplied=str(o.SumApplied),
            InvType=o.InvType,
        )

    async def patch(self, doc_entry: int, line_num: int, data: OutgoingPaymentLinePatchBody) -> OutgoingPaymentLineResponse:
        try:
            o = await VPM1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except VPM1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.DocNum is not None:
            o.DocNum = data.DocNum
        if data.SumApplied is not None:
            o.SumApplied = Decimal(str(data.SumApplied))
        if data.InvType is not None:
            o.InvType = int(data.InvType)
        await o.asave()
        return OutgoingPaymentLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            DocNum=o.DocNum,
            SumApplied=str(o.SumApplied),
            InvType=o.InvType,
        )

    async def delete(self, doc_entry: int, line_num: int) -> OutgoingPaymentLineResponse:
        try:
            o = await VPM1.objects.select_related("header").aget(header_id=doc_entry, LineNum=int(line_num))
        except VPM1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = OutgoingPaymentLineResponse(
            DocEntry=o.header_id,
            LineNum=o.LineNum,
            DocNum=o.DocNum,
            SumApplied=str(o.SumApplied),
            InvType=o.InvType,
        )
        await o.adelete()
        return rep


class TaxCodeCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> TaxCodePage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = OSTC.objects.all().order_by("Code")
        if search_prefix:
            qs = qs.filter(Q(Code__istartswith=search_prefix) | Q(Name__istartswith=search_prefix))
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return TaxCodePage(
            items=[
                TaxCodeResponse(Code=o.Code, Name=o.Name, Rate=str(o.Rate), Account=o.Account or "")
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: TaxCodeCreateBody) -> TaxCodeResponse:
        o = OSTC(
            Code=data.Code.strip(),
            Name=data.Name.strip(),
            Rate=Decimal(str(data.Rate or "0")),
            Account=(data.Account or "").strip(),
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate tax Code.")
        return TaxCodeResponse(Code=o.Code, Name=o.Name, Rate=str(o.Rate), Account=o.Account or "")


class TaxCodeDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, code: str) -> TaxCodeResponse:
        try:
            o = await OSTC.objects.aget(pk=code.strip())
        except OSTC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return TaxCodeResponse(Code=o.Code, Name=o.Name, Rate=str(o.Rate), Account=o.Account or "")

    async def patch(self, code: str, data: TaxCodePatchBody) -> TaxCodeResponse:
        try:
            o = await OSTC.objects.aget(pk=code.strip())
        except OSTC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.Name is not None:
            o.Name = data.Name.strip()
        if data.Rate is not None:
            o.Rate = Decimal(str(data.Rate))
        if data.Account is not None:
            o.Account = data.Account.strip()
        await o.asave()
        return TaxCodeResponse(Code=o.Code, Name=o.Name, Rate=str(o.Rate), Account=o.Account or "")

    async def delete(self, code: str) -> TaxCodeResponse:
        try:
            o = await OSTC.objects.aget(pk=code.strip())
        except OSTC.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = TaxCodeResponse(Code=o.Code, Name=o.Name, Rate=str(o.Rate), Account=o.Account or "")
        await o.adelete()
        return rep


class FinancialPeriodCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> FinancialPeriodPage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = OFPR.objects.all().order_by("-AbsEntry")
        if search_prefix:
            qs = qs.filter(PeriodCode__istartswith=search_prefix)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return FinancialPeriodPage(
            items=[
                FinancialPeriodResponse(
                    AbsEntry=o.AbsEntry,
                    PeriodCode=o.PeriodCode,
                    F_RefDate=o.F_RefDate,
                    T_RefDate=o.T_RefDate,
                    PeriodStat=o.PeriodStat,
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: FinancialPeriodCreateBody) -> FinancialPeriodResponse:
        o = OFPR(
            PeriodCode=data.PeriodCode.strip(),
            F_RefDate=data.F_RefDate,
            T_RefDate=data.T_RefDate,
            PeriodStat=(data.PeriodStat or "Unlocked").strip(),
        )
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate PeriodCode.")
        return FinancialPeriodResponse(
            AbsEntry=o.AbsEntry,
            PeriodCode=o.PeriodCode,
            F_RefDate=o.F_RefDate,
            T_RefDate=o.T_RefDate,
            PeriodStat=o.PeriodStat,
        )


class FinancialPeriodDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, abs_entry: int) -> FinancialPeriodResponse:
        try:
            o = await OFPR.objects.aget(pk=abs_entry)
        except OFPR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return FinancialPeriodResponse(
            AbsEntry=o.AbsEntry,
            PeriodCode=o.PeriodCode,
            F_RefDate=o.F_RefDate,
            T_RefDate=o.T_RefDate,
            PeriodStat=o.PeriodStat,
        )

    async def patch(self, abs_entry: int, data: FinancialPeriodPatchBody) -> FinancialPeriodResponse:
        try:
            o = await OFPR.objects.aget(pk=abs_entry)
        except OFPR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.PeriodCode is not None:
            o.PeriodCode = data.PeriodCode.strip()
        if data.F_RefDate is not None:
            o.F_RefDate = data.F_RefDate
        if data.T_RefDate is not None:
            o.T_RefDate = data.T_RefDate
        if data.PeriodStat is not None:
            o.PeriodStat = data.PeriodStat.strip()
        await o.asave()
        return FinancialPeriodResponse(
            AbsEntry=o.AbsEntry,
            PeriodCode=o.PeriodCode,
            F_RefDate=o.F_RefDate,
            T_RefDate=o.T_RefDate,
            PeriodStat=o.PeriodStat,
        )

    async def delete(self, abs_entry: int) -> FinancialPeriodResponse:
        try:
            o = await OFPR.objects.aget(pk=abs_entry)
        except OFPR.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = FinancialPeriodResponse(
            AbsEntry=o.AbsEntry,
            PeriodCode=o.PeriodCode,
            F_RefDate=o.F_RefDate,
            T_RefDate=o.T_RefDate,
            PeriodStat=o.PeriodStat,
        )
        await o.adelete()
        return rep


class BudgetSetupCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BudgetSetupPage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qs = OBGT.objects.select_related("AcctCode").all().order_by("AcctCode_id")
        if search_prefix:
            qs = qs.filter(AcctCode_id__istartswith=search_prefix)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return BudgetSetupPage(
            items=[
                BudgetSetupResponse(AcctCode=o.AcctCode_id, BudgTotal=str(o.BudgTotal)) for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: BudgetSetupCreateBody) -> BudgetSetupResponse:
        if not await OACT.objects.filter(pk=data.AcctCode.strip()).aexists():
            raise BadRequest(detail="AcctCode must exist in OACT.")
        o = OBGT(AcctCode_id=data.AcctCode.strip(), BudgTotal=Decimal(str(data.BudgTotal or "0")))
        try:
            await o.asave()
        except IntegrityError:
            raise BadRequest(detail="Budget already exists for this AcctCode.")
        return BudgetSetupResponse(AcctCode=o.AcctCode_id, BudgTotal=str(o.BudgTotal))


class BudgetSetupDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, acct_code: str) -> BudgetSetupResponse:
        try:
            o = await OBGT.objects.aget(pk=acct_code.strip())
        except OBGT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return BudgetSetupResponse(AcctCode=o.AcctCode_id, BudgTotal=str(o.BudgTotal))

    async def patch(self, acct_code: str, data: BudgetSetupPatchBody) -> BudgetSetupResponse:
        try:
            o = await OBGT.objects.aget(pk=acct_code.strip())
        except OBGT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.BudgTotal is not None:
            o.BudgTotal = Decimal(str(data.BudgTotal))
        await o.asave()
        return BudgetSetupResponse(AcctCode=o.AcctCode_id, BudgTotal=str(o.BudgTotal))

    async def delete(self, acct_code: str) -> BudgetSetupResponse:
        try:
            o = await OBGT.objects.aget(pk=acct_code.strip())
        except OBGT.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = BudgetSetupResponse(AcctCode=o.AcctCode_id, BudgTotal=str(o.BudgTotal))
        await o.adelete()
        return rep


def _norm_prc(prc_code: str) -> str:
    return "" if prc_code.strip() == "-" else prc_code.strip()


class BudgetLineCollection(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self) -> BudgetLinePage:
        limit, offset, search_prefix = _read_pagination(self.request)
        qd = getattr(self.request, "query", None) or {}
        raw_ac = (qd.get("acct_code") or "").strip()
        raw_m = (qd.get("month") or "").strip()
        month = int(raw_m) if raw_m else None
        qs = BGT1.objects.all().order_by("header_id", "Month", "PrcCode")
        if raw_ac:
            qs = qs.filter(header_id=raw_ac)
        if month is not None:
            qs = qs.filter(Month=month)
        if search_prefix:
            qs = qs.filter(PrcCode__istartswith=search_prefix)
        rows = await sync_to_async(list)(qs[offset : offset + limit])
        return BudgetLinePage(
            items=[
                BudgetLineResponse(
                    AcctCode=o.header_id,
                    Month=o.Month,
                    PrcCode=o.PrcCode or "",
                    PlannedAmt=str(o.PlannedAmt),
                )
                for o in rows
            ],
            limit=limit,
            offset=offset,
        )

    async def post(self, data: BudgetLineCreateBody) -> BudgetLineResponse:
        if not await OBGT.objects.filter(pk=data.AcctCode.strip()).aexists():
            raise BadRequest(detail="Create OBGT budget setup for this AcctCode first.")
        prc = (data.PrcCode or "").strip()
        line = BGT1(
            header_id=data.AcctCode.strip(),
            Month=int(data.Month),
            PrcCode=prc,
            PlannedAmt=Decimal(str(data.PlannedAmt)),
        )
        try:
            await line.asave()
        except IntegrityError:
            raise BadRequest(detail="Duplicate budget line.")
        return BudgetLineResponse(
            AcctCode=line.header_id,
            Month=line.Month,
            PrcCode=line.PrcCode or "",
            PlannedAmt=str(line.PlannedAmt),
        )


class BudgetLineDetail(APIView):
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    async def get(self, acct_code: str, month: int, prc_code: str) -> BudgetLineResponse:
        pc = _norm_prc(prc_code)
        try:
            o = await BGT1.objects.aget(header_id=acct_code.strip(), Month=int(month), PrcCode=pc)
        except BGT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        return BudgetLineResponse(
            AcctCode=o.header_id,
            Month=o.Month,
            PrcCode=o.PrcCode or "",
            PlannedAmt=str(o.PlannedAmt),
        )

    async def patch(self, acct_code: str, month: int, prc_code: str, data: BudgetLinePatchBody) -> BudgetLineResponse:
        pc = _norm_prc(prc_code)
        try:
            o = await BGT1.objects.aget(header_id=acct_code.strip(), Month=int(month), PrcCode=pc)
        except BGT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        if data.PlannedAmt is not None:
            o.PlannedAmt = Decimal(str(data.PlannedAmt))
        await o.asave()
        return BudgetLineResponse(
            AcctCode=o.header_id,
            Month=o.Month,
            PrcCode=o.PrcCode or "",
            PlannedAmt=str(o.PlannedAmt),
        )

    async def delete(self, acct_code: str, month: int, prc_code: str) -> BudgetLineResponse:
        pc = _norm_prc(prc_code)
        try:
            o = await BGT1.objects.aget(header_id=acct_code.strip(), Month=int(month), PrcCode=pc)
        except BGT1.DoesNotExist:
            raise NotFound(detail="খুঁজে পাওয়া যায়নি।")
        rep = BudgetLineResponse(
            AcctCode=o.header_id,
            Month=o.Month,
            PrcCode=o.PrcCode or "",
            PlannedAmt=str(o.PlannedAmt),
        )
        await o.adelete()
        return rep


def attach_finance_routes(api: BoltAPI) -> None:
    tag = ["finance"]
    p = FINANCE_API_PREFIX
    api.view(p + "/chart-of-accounts", methods=["GET", "POST"], status_code=200, tags=tag)(GlAccountCollection)
    api.view(p + "/chart-of-accounts/{acct_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(GlAccountDetail)
    api.view(p + "/profit-centers", methods=["GET", "POST"], status_code=200, tags=tag)(ProfitCenterCollection)
    api.view(p + "/profit-centers/{prc_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(ProfitCenterDetail)
    api.view(p + "/journal-entries", methods=["GET", "POST"], status_code=200, tags=tag)(JournalEntryCollection)
    api.view(p + "/journal-entries/{trans_id}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(JournalEntryDetail)
    api.view(p + "/journal-entry-lines", methods=["GET", "POST"], status_code=200, tags=tag)(JournalEntryLineCollection)
    api.view(
        p + "/journal-entry-lines/{trans_id}/{line_id}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(JournalEntryLineDetail)
    api.view(p + "/incoming-payments", methods=["GET", "POST"], status_code=200, tags=tag)(IncomingPaymentCollection)
    api.view(p + "/incoming-payments/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        IncomingPaymentDetail
    )
    api.view(p + "/incoming-payment-lines", methods=["GET", "POST"], status_code=200, tags=tag)(IncomingPaymentLineCollection)
    api.view(
        p + "/incoming-payment-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(IncomingPaymentLineDetail)
    api.view(p + "/oact", methods=["GET", "POST"], status_code=200, tags=tag)(GlAccountCollection)
    api.view(p + "/oact/{acct_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(GlAccountDetail)
    api.view(p + "/oprc", methods=["GET", "POST"], status_code=200, tags=tag)(ProfitCenterCollection)
    api.view(p + "/oprc/{prc_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(ProfitCenterDetail)
    api.view(p + "/ojdt", methods=["GET", "POST"], status_code=200, tags=tag)(JournalEntryCollection)
    api.view(p + "/ojdt/{trans_id}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(JournalEntryDetail)
    api.view(p + "/jdt1", methods=["GET", "POST"], status_code=200, tags=tag)(JournalEntryLineCollection)
    api.view(p + "/jdt1/{trans_id}/{line_id}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        JournalEntryLineDetail
    )
    api.view(p + "/orct", methods=["GET", "POST"], status_code=200, tags=tag)(IncomingPaymentCollection)
    api.view(p + "/orct/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(IncomingPaymentDetail)
    api.view(p + "/rct1", methods=["GET", "POST"], status_code=200, tags=tag)(IncomingPaymentLineCollection)
    api.view(p + "/rct1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        IncomingPaymentLineDetail
    )
    api.view(p + "/outgoing-payments", methods=["GET", "POST"], status_code=200, tags=tag)(OutgoingPaymentCollection)
    api.view(p + "/outgoing-payments/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        OutgoingPaymentDetail
    )
    api.view(p + "/outgoing-payment-lines", methods=["GET", "POST"], status_code=200, tags=tag)(OutgoingPaymentLineCollection)
    api.view(
        p + "/outgoing-payment-lines/{doc_entry}/{line_num}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(OutgoingPaymentLineDetail)
    api.view(p + "/tax-codes", methods=["GET", "POST"], status_code=200, tags=tag)(TaxCodeCollection)
    api.view(p + "/tax-codes/{code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(TaxCodeDetail)
    api.view(p + "/financial-periods", methods=["GET", "POST"], status_code=200, tags=tag)(FinancialPeriodCollection)
    api.view(
        p + "/financial-periods/{abs_entry}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(FinancialPeriodDetail)
    api.view(p + "/budget-setups", methods=["GET", "POST"], status_code=200, tags=tag)(BudgetSetupCollection)
    api.view(p + "/budget-setups/{acct_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        BudgetSetupDetail
    )
    api.view(p + "/budget-lines", methods=["GET", "POST"], status_code=200, tags=tag)(BudgetLineCollection)
    api.view(
        p + "/budget-lines/{acct_code}/{month}/{prc_code}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(BudgetLineDetail)
    api.view(p + "/ovpm", methods=["GET", "POST"], status_code=200, tags=tag)(OutgoingPaymentCollection)
    api.view(p + "/ovpm/{doc_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(OutgoingPaymentDetail)
    api.view(p + "/vpm1", methods=["GET", "POST"], status_code=200, tags=tag)(OutgoingPaymentLineCollection)
    api.view(p + "/vpm1/{doc_entry}/{line_num}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(
        OutgoingPaymentLineDetail
    )
    api.view(p + "/ostc", methods=["GET", "POST"], status_code=200, tags=tag)(TaxCodeCollection)
    api.view(p + "/ostc/{code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(TaxCodeDetail)
    api.view(p + "/ofpr", methods=["GET", "POST"], status_code=200, tags=tag)(FinancialPeriodCollection)
    api.view(p + "/ofpr/{abs_entry}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(FinancialPeriodDetail)
    api.view(p + "/obgt", methods=["GET", "POST"], status_code=200, tags=tag)(BudgetSetupCollection)
    api.view(p + "/obgt/{acct_code}", methods=["GET", "PATCH", "DELETE"], status_code=200, tags=tag)(BudgetSetupDetail)
    api.view(p + "/bgt1", methods=["GET", "POST"], status_code=200, tags=tag)(BudgetLineCollection)
    api.view(
        p + "/bgt1/{acct_code}/{month}/{prc_code}",
        methods=["GET", "PATCH", "DELETE"],
        status_code=200,
        tags=tag,
    )(BudgetLineDetail)

