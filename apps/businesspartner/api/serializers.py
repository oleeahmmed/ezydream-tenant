"""
Business partner — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।
"""

from __future__ import annotations

from typing import Annotated

from django_bolt.serializers import Serializer, field
from django_bolt.serializers.nested import Nested

PAGE_MAX_ITEMS = 100


class BPGroupResponse(Serializer):
    GroupCode: int
    GroupName: str
    GroupType: str
    Canceled: str




class BPGroupPage(Serializer):
    items: Annotated[list[BPGroupResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class BPGroupCreateBody(Serializer):
    GroupCode: int
    GroupName: str
    GroupType: str = field(default="B")




class BPGroupPatchBody(Serializer):
    GroupName: str | None = field(default=None)
    GroupType: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class BusinessPartnerResponse(Serializer):
    CardCode: str
    CardName: str
    CardType: str
    GroupCode: int | None
    CardFName: str
    CntctPrsn: str
    Phone1: str
    Phone2: str
    Fax: str
    Cellular: str
    E_Mail: str
    Website: str
    LicTradNum: str
    CreditLine: str
    DebtLine: str
    Balance: str
    OrdersBal: str
    DNotesBal: str
    Currency: str
    PayTermsGrpCode: int | None
    DfltWhs: str
    ShipToDef: str
    BillToDef: str
    SlpCode: int | None
    Comments: str
    ValidFor: str
    Frozen: str
    Canceled: str




class BusinessPartnerPage(Serializer):
    items: Annotated[list[BusinessPartnerResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class BusinessPartnerCreateBody(Serializer):
    CardCode: str
    CardName: str
    CardType: str = field(default="C")
    GroupCode: int | None = field(default=None)
    CardFName: str = field(default="")
    CntctPrsn: str = field(default="")
    Phone1: str = field(default="")
    Phone2: str = field(default="")
    Fax: str = field(default="")
    Cellular: str = field(default="")
    E_Mail: str = field(default="")
    Website: str = field(default="")
    LicTradNum: str = field(default="")
    CreditLine: str = field(default="0")
    DebtLine: str = field(default="0")
    Balance: str = field(default="0")
    OrdersBal: str = field(default="0")
    DNotesBal: str = field(default="0")
    Currency: str = field(default="")
    PayTermsGrpCode: int | None = field(default=None)
    DfltWhs: str = field(default="")
    ShipToDef: str = field(default="")
    BillToDef: str = field(default="")
    SlpCode: int | None = field(default=None)
    Comments: str = field(default="")
    ValidFor: str = field(default="Y")
    Frozen: str = field(default="N")




class BusinessPartnerPatchBody(Serializer):
    CardName: str | None = field(default=None)
    CardType: str | None = field(default=None)
    GroupCode: int | None = field(default=None)
    CardFName: str | None = field(default=None)
    CntctPrsn: str | None = field(default=None)
    Phone1: str | None = field(default=None)
    Phone2: str | None = field(default=None)
    Fax: str | None = field(default=None)
    Cellular: str | None = field(default=None)
    E_Mail: str | None = field(default=None)
    Website: str | None = field(default=None)
    LicTradNum: str | None = field(default=None)
    CreditLine: str | None = field(default=None)
    DebtLine: str | None = field(default=None)
    Balance: str | None = field(default=None)
    OrdersBal: str | None = field(default=None)
    DNotesBal: str | None = field(default=None)
    Currency: str | None = field(default=None)
    PayTermsGrpCode: int | None = field(default=None)
    DfltWhs: str | None = field(default=None)
    ShipToDef: str | None = field(default=None)
    BillToDef: str | None = field(default=None)
    SlpCode: int | None = field(default=None)
    Comments: str | None = field(default=None)
    ValidFor: str | None = field(default=None)
    Frozen: str | None = field(default=None)
    Canceled: str | None = field(default=None)




class BPAddressResponse(Serializer):
    CardCode: str
    Address: str
    Street: str
    Block: str
    City: str
    County: str
    ZipCode: str
    Country: str
    State: str
    Building: str
    AdresType: str
    Canceled: str




class BPAddressPage(Serializer):
    items: Annotated[list[BPAddressResponse], Nested(max_items=PAGE_MAX_ITEMS)]
    limit: int
    offset: int




class BPAddressCreateBody(Serializer):
    Address: str
    Street: str = field(default="")
    Block: str = field(default="")
    City: str = field(default="")
    County: str = field(default="")
    ZipCode: str = field(default="")
    Country: str = field(default="")
    State: str = field(default="")
    Building: str = field(default="")
    AdresType: str = field(default="S")
    Canceled: str = field(default="N")




class BPAddressPatchBody(Serializer):
    Street: str | None = field(default=None)
    Block: str | None = field(default=None)
    City: str | None = field(default=None)
    County: str | None = field(default=None)
    ZipCode: str | None = field(default=None)
    Country: str | None = field(default=None)
    State: str | None = field(default=None)
    Building: str | None = field(default=None)
    AdresType: str | None = field(default=None)
    Canceled: str | None = field(default=None)
