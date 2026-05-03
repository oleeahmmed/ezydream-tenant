"""
Post inventory movements (OINM + OITW/OITM) when operational documents change.

Uses ``post_oinm_and_apply_stock`` / ``reverse_oinm_stock`` from ``stock_posting``.
"""

from __future__ import annotations

from datetime import datetime, time
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.core import b1_inventory_transtype as tt
from apps.inventory.models import OINM
from apps.inventory.services.stock_posting import post_oinm_and_apply_stock, reverse_oinm_stock


def _doc_dt(d) -> datetime:
    if d is None:
        return timezone.now()
    dt = datetime.combine(d, time.min)
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def _cancel_open_movements(trans_type: int, doc_entry: int, line_num: int) -> None:
    qs = OINM.objects.select_for_update().filter(
        TransType=trans_type,
        DocEntry=doc_entry,
        DocLineNum=line_num,
        Canceled="N",
    )
    for row in qs:
        reverse_oinm_stock(row)
        row.Canceled = "Y"
        row.save(update_fields=["Canceled"])


@transaction.atomic
def sync_delivery_line_stock(header_id: int, line_num: int) -> None:
    from apps.sales.models import DLN1

    line = DLN1.objects.select_related("header").get(header_id=header_id, LineNum=line_num)
    hdr = line.header
    _cancel_open_movements(tt.TRANS_DELIVERY, int(hdr.DocEntry), int(line.LineNum))
    if line.Canceled == "N" and hdr.Canceled == "N" and hdr.DocStatus == "O":
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_DELIVERY,
            item_code=line.ItemCode,
            warehouse=line.WhsCode,
            in_qty=Decimal("0"),
            out_qty=line.Quantity,
            price=line.Price,
            base_ref=f"ODLN-{hdr.DocEntry}",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=int(line.LineNum),
            trans_value=line.LineTotal,
        )


@transaction.atomic
def sync_return_line_stock(header_id: int, line_num: int) -> None:
    from apps.sales.models import RDN1

    line = RDN1.objects.select_related("header").get(header_id=header_id, LineNum=line_num)
    hdr = line.header
    _cancel_open_movements(tt.TRANS_GOODS_RETURN, int(hdr.DocEntry), int(line.LineNum))
    if line.Canceled == "N" and hdr.Canceled == "N" and hdr.DocStatus == "O":
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_GOODS_RETURN,
            item_code=line.ItemCode,
            warehouse=line.WhsCode,
            in_qty=line.Quantity,
            out_qty=Decimal("0"),
            price=line.Price,
            base_ref=f"ORDN-{hdr.DocEntry}",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=int(line.LineNum),
            trans_value=line.LineTotal,
        )


@transaction.atomic
def sync_grpo_line_stock(header_id: int, line_num: int) -> None:
    from apps.purchase.models import OPDN, PDN1

    line = PDN1.objects.select_related("header").get(header_id=header_id, LineNum=line_num)
    hdr: OPDN = line.header
    _cancel_open_movements(tt.TRANS_GRPO, int(hdr.DocEntry), int(line.LineNum))
    if line.Canceled == "N" and hdr.Canceled == "N" and hdr.DocStatus == "O":
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_GRPO,
            item_code=line.ItemCode,
            warehouse=line.WhsCode,
            in_qty=line.Quantity,
            out_qty=Decimal("0"),
            price=line.Price,
            base_ref=f"OPDN-{hdr.DocEntry}",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=int(line.LineNum),
            trans_value=line.LineTotal,
        )


@transaction.atomic
def sync_vendor_return_line_stock(header_id: int, line_num: int) -> None:
    from apps.purchase.models import ORPC, RPC1

    line = RPC1.objects.select_related("header").get(header_id=header_id, LineNum=line_num)
    hdr: ORPC = line.header
    _cancel_open_movements(tt.TRANS_VENDOR_GOODS_RETURN, int(hdr.DocEntry), int(line.LineNum))
    if line.Canceled == "N" and hdr.Canceled == "N" and hdr.DocStatus == "O":
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_VENDOR_GOODS_RETURN,
            item_code=line.ItemCode,
            warehouse=line.WhsCode,
            in_qty=Decimal("0"),
            out_qty=line.Quantity,
            price=line.Price,
            base_ref=f"ORPC-{hdr.DocEntry}",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=int(line.LineNum),
            trans_value=line.LineTotal,
        )


@transaction.atomic
def sync_goods_receipt_line_stock(header_id: int, line_num: int) -> None:
    from apps.inventory.models import IGN1

    line = IGN1.objects.select_related("header").get(header_id=header_id, LineNum=line_num)
    hdr = line.header
    _cancel_open_movements(tt.TRANS_GOODS_RECEIPT, int(hdr.DocEntry), int(line.LineNum))
    if line.Canceled == "N" and hdr.Canceled == "N" and hdr.DocStatus == "O":
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_GOODS_RECEIPT,
            item_code=line.ItemCode,
            warehouse=line.WhsCode,
            in_qty=line.Quantity,
            out_qty=Decimal("0"),
            price=line.Price,
            base_ref=f"OIGN-{hdr.DocEntry}",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=int(line.LineNum),
            trans_value=line.LineTotal,
        )


@transaction.atomic
def sync_goods_issue_line_stock(header_id: int, line_num: int) -> None:
    from apps.inventory.models import IGE1

    line = IGE1.objects.select_related("header").get(header_id=header_id, LineNum=line_num)
    hdr = line.header
    _cancel_open_movements(tt.TRANS_GOODS_ISSUE, int(hdr.DocEntry), int(line.LineNum))
    if line.Canceled == "N" and hdr.Canceled == "N" and hdr.DocStatus == "O":
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_GOODS_ISSUE,
            item_code=line.ItemCode,
            warehouse=line.WhsCode,
            in_qty=Decimal("0"),
            out_qty=line.Quantity,
            price=line.Price,
            base_ref=f"OIGE-{hdr.DocEntry}",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=int(line.LineNum),
            trans_value=line.LineTotal,
        )


@transaction.atomic
def sync_transfer_line_stock(header_id: int, line_num: int) -> None:
    from apps.inventory.models import WTR1

    line = WTR1.objects.select_related("header").get(header_id=header_id, LineNum=line_num)
    hdr = line.header
    base_id = int(line.LineNum) * 1000
    _cancel_open_movements(tt.TRANS_WAREHOUSE_TRANSFER, int(hdr.DocEntry), base_id + 1)
    _cancel_open_movements(tt.TRANS_WAREHOUSE_TRANSFER, int(hdr.DocEntry), base_id + 2)
    if line.Canceled == "N" and hdr.Canceled == "N" and hdr.DocStatus == "O":
        from_wh = (line.FromWhsCod or "").strip() or (line.WhsCode or "").strip()
        to_wh = (line.WhsCode or "").strip()
        if not from_wh or not to_wh:
            raise ValidationError("Transfer line needs FromWhsCod and WhsCode.")
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_WAREHOUSE_TRANSFER,
            item_code=line.ItemCode,
            warehouse=from_wh,
            in_qty=Decimal("0"),
            out_qty=line.Quantity,
            price=line.Price,
            base_ref=f"OWTR-{hdr.DocEntry}-OUT",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=base_id + 1,
            trans_value=line.LineTotal,
        )
        post_oinm_and_apply_stock(
            trans_type=tt.TRANS_WAREHOUSE_TRANSFER,
            item_code=line.ItemCode,
            warehouse=to_wh,
            in_qty=line.Quantity,
            out_qty=Decimal("0"),
            price=line.Price,
            base_ref=f"OWTR-{hdr.DocEntry}-IN",
            doc_time=_doc_dt(hdr.DocDate),
            doc_entry=int(hdr.DocEntry),
            doc_line_num=base_id + 2,
            trans_value=line.LineTotal,
        )


@transaction.atomic
def release_all_document_lines_for_header(trans_type: int, doc_entry: int) -> None:
    for row in OINM.objects.select_for_update().filter(TransType=trans_type, DocEntry=doc_entry, Canceled="N"):
        reverse_oinm_stock(row)
        row.Canceled = "Y"
        row.save(update_fields=["Canceled"])


def resync_all_delivery_lines(doc_entry: int) -> None:
    from apps.sales.models import DLN1

    for ln in DLN1.objects.filter(header_id=doc_entry).values_list("LineNum", flat=True):
        sync_delivery_line_stock(doc_entry, int(ln))


def resync_all_return_lines(doc_entry: int) -> None:
    from apps.sales.models import RDN1

    for ln in RDN1.objects.filter(header_id=doc_entry).values_list("LineNum", flat=True):
        sync_return_line_stock(doc_entry, int(ln))


def resync_all_grpo_lines(doc_entry: int) -> None:
    from apps.purchase.models import PDN1

    for ln in PDN1.objects.filter(header_id=doc_entry).values_list("LineNum", flat=True):
        sync_grpo_line_stock(doc_entry, int(ln))


def resync_all_vendor_return_lines(doc_entry: int) -> None:
    from apps.purchase.models import RPC1

    for ln in RPC1.objects.filter(header_id=doc_entry).values_list("LineNum", flat=True):
        sync_vendor_return_line_stock(doc_entry, int(ln))


def resync_all_ign_lines(doc_entry: int) -> None:
    from apps.inventory.models import IGN1

    for ln in IGN1.objects.filter(header_id=doc_entry).values_list("LineNum", flat=True):
        sync_goods_receipt_line_stock(doc_entry, int(ln))


def resync_all_ige_lines(doc_entry: int) -> None:
    from apps.inventory.models import IGE1

    for ln in IGE1.objects.filter(header_id=doc_entry).values_list("LineNum", flat=True):
        sync_goods_issue_line_stock(doc_entry, int(ln))


def resync_all_wtr_lines(doc_entry: int) -> None:
    from apps.inventory.models import WTR1

    for ln in WTR1.objects.filter(header_id=doc_entry).values_list("LineNum", flat=True):
        sync_transfer_line_stock(doc_entry, int(ln))
