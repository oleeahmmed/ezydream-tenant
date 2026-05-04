"""
Finance — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

PAGE_MAX_ITEMS = 100

class GlAccountResponse(Serializer):
    AcctCode: str
    AcctName: str
    CurrTotal: str
    GroupMask: int
    FatherNum: str
    Postable: str
    LocCash: str
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class GlAccountPage(Serializer):
    items: Annotated[list[GlAccountResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class GlAccountCreateBody(Serializer):
    AcctCode: str
    AcctName: str
    CurrTotal: str = field(default="0")
    GroupMask: int
    FatherNum: str = field(default="")
    Postable: str = field(default="Y")
    LocCash: str = field(default="N")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class GlAccountPatchBody(Serializer):
    AcctName: str | None = field(default=None)
    CurrTotal: str | None = field(default=None)
    GroupMask: int | None = field(default=None)
    FatherNum: str | None = field(default=None)
    Postable: str | None = field(default=None)
    LocCash: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)


class ProfitCenterResponse(Serializer):
    PrcCode: str
    PrcName: str
    DimCode: int
    Active: str
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class ProfitCenterPage(Serializer):
    items: Annotated[list[ProfitCenterResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class ProfitCenterCreateBody(Serializer):
    PrcCode: str
    PrcName: str
    DimCode: int
    Active: str = field(default="Y")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class ProfitCenterPatchBody(Serializer):
    PrcName: str | None = field(default=None)
    DimCode: int | None = field(default=None)
    Active: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)


class JournalEntryResponse(Serializer):
    TransId: int
    BaseRef: str
    RefDate: date
    TransType: int
    Memo: str
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class JournalEntryPage(Serializer):
    items: Annotated[list[JournalEntryResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class JournalEntryCreateBody(Serializer):
    BaseRef: str = field(default="")
    RefDate: date
    TransType: int
    Memo: str = field(default="")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class JournalEntryPatchBody(Serializer):
    BaseRef: str | None = field(default=None)
    RefDate: date | None = field(default=None)
    TransType: int | None = field(default=None)
    Memo: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)


class JournalEntryLineResponse(Serializer):
    TransId: int
    Line_ID: int
    Account: str
    ShortName: str
    Debit: str
    Credit: str
    ProfitCode: str


class JournalEntryLinePage(Serializer):
    items: Annotated[list[JournalEntryLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class JournalEntryLineCreateBody(Serializer):
    TransId: int
    Line_ID: int
    Account: str
    ShortName: str = field(default="")
    Debit: str = field(default="0")
    Credit: str = field(default="0")
    ProfitCode: str = field(default="")


class JournalEntryLinePatchBody(Serializer):
    Account: str | None = field(default=None)
    ShortName: str | None = field(default=None)
    Debit: str | None = field(default=None)
    Credit: str | None = field(default=None)
    ProfitCode: str | None = field(default=None)


class IncomingPaymentResponse(Serializer):
    DocEntry: int
    CardCode: str
    CardName: str
    DocDate: date
    CashAcct: str
    CheckAcct: str
    DocTotal: str
    CashSum: str
    DocStatus: str = field(default="O")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class IncomingPaymentPage(Serializer):
    items: Annotated[list[IncomingPaymentResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class IncomingPaymentCreateBody(Serializer):
    CardCode: str
    CardName: str = field(default="")
    DocDate: date
    CashAcct: str = field(default="")
    CheckAcct: str = field(default="")
    DocTotal: str = field(default="0")
    CashSum: str = field(default="0")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class IncomingPaymentPatchBody(Serializer):
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    CashAcct: str | None = field(default=None)
    CheckAcct: str | None = field(default=None)
    DocTotal: str | None = field(default=None)
    CashSum: str | None = field(default=None)
    DocStatus: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)


class IncomingPaymentLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    DocNum: int | None = field(default=None)
    SumApplied: str
    InvType: int


class IncomingPaymentLinePage(Serializer):
    items: Annotated[list[IncomingPaymentLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class IncomingPaymentLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    DocNum: int | None = field(default=None)
    SumApplied: str
    InvType: int = field(default=0)


class IncomingPaymentLinePatchBody(Serializer):
    DocNum: int | None = field(default=None)
    SumApplied: str | None = field(default=None)
    InvType: int | None = field(default=None)


class OutgoingPaymentResponse(Serializer):
    DocEntry: int
    CardCode: str
    CardName: str
    DocDate: date
    BankAcct: str
    CashSum: str
    TrsfrSum: str
    DocTotal: str
    DocStatus: str = field(default="O")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class OutgoingPaymentPage(Serializer):
    items: Annotated[list[OutgoingPaymentResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class OutgoingPaymentCreateBody(Serializer):
    CardCode: str
    CardName: str = field(default="")
    DocDate: date
    BankAcct: str = field(default="")
    CashSum: str = field(default="0")
    TrsfrSum: str = field(default="0")
    DocTotal: str = field(default="0")
    U_UserFld1: str = field(default="")
    U_UserFld2: str = field(default="")


class OutgoingPaymentPatchBody(Serializer):
    CardCode: str | None = field(default=None)
    CardName: str | None = field(default=None)
    DocDate: date | None = field(default=None)
    BankAcct: str | None = field(default=None)
    CashSum: str | None = field(default=None)
    TrsfrSum: str | None = field(default=None)
    DocTotal: str | None = field(default=None)
    DocStatus: str | None = field(default=None)
    U_UserFld1: str | None = field(default=None)
    U_UserFld2: str | None = field(default=None)


class OutgoingPaymentLineResponse(Serializer):
    DocEntry: int
    LineNum: int
    DocNum: int | None = field(default=None)
    SumApplied: str
    InvType: int


class OutgoingPaymentLinePage(Serializer):
    items: Annotated[list[OutgoingPaymentLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class OutgoingPaymentLineCreateBody(Serializer):
    DocEntry: int
    LineNum: int
    DocNum: int | None = field(default=None)
    SumApplied: str
    InvType: int = field(default=0)


class OutgoingPaymentLinePatchBody(Serializer):
    DocNum: int | None = field(default=None)
    SumApplied: str | None = field(default=None)
    InvType: int | None = field(default=None)


class TaxCodeResponse(Serializer):
    Code: str
    Name: str
    Rate: str
    Account: str


class TaxCodePage(Serializer):
    items: Annotated[list[TaxCodeResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class TaxCodeCreateBody(Serializer):
    Code: str
    Name: str
    Rate: str = field(default="0")
    Account: str = field(default="")


class TaxCodePatchBody(Serializer):
    Name: str | None = field(default=None)
    Rate: str | None = field(default=None)
    Account: str | None = field(default=None)


class FinancialPeriodResponse(Serializer):
    AbsEntry: int
    PeriodCode: str
    F_RefDate: date
    T_RefDate: date
    PeriodStat: str


class FinancialPeriodPage(Serializer):
    items: Annotated[list[FinancialPeriodResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class FinancialPeriodCreateBody(Serializer):
    PeriodCode: str
    F_RefDate: date
    T_RefDate: date
    PeriodStat: str = field(default="Unlocked")


class FinancialPeriodPatchBody(Serializer):
    PeriodCode: str | None = field(default=None)
    F_RefDate: date | None = field(default=None)
    T_RefDate: date | None = field(default=None)
    PeriodStat: str | None = field(default=None)


class BudgetSetupResponse(Serializer):
    AcctCode: str
    BudgTotal: str


class BudgetSetupPage(Serializer):
    items: Annotated[list[BudgetSetupResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class BudgetSetupCreateBody(Serializer):
    AcctCode: str
    BudgTotal: str = field(default="0")


class BudgetSetupPatchBody(Serializer):
    BudgTotal: str | None = field(default=None)


class BudgetLineResponse(Serializer):
    AcctCode: str
    Month: int
    PrcCode: str
    PlannedAmt: str


class BudgetLinePage(Serializer):
    items: Annotated[list[BudgetLineResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int


class BudgetLineCreateBody(Serializer):
    AcctCode: str
    Month: int
    PrcCode: str = field(default="")
    PlannedAmt: str


class BudgetLinePatchBody(Serializer):
    PrcCode: str | None = field(default=None)
    PlannedAmt: str | None = field(default=None)


