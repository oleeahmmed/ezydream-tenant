import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { apiFetch } from "../../lib/apiFetch";
import { fetchBusinessPartner } from "../../lib/businessPartnerApi";
import { useWorkspace } from "../../workspace/WorkspaceContext";
import { BpSearchModal } from "../../ui/BpSearchModal";
import { DocumentFindModal } from "../../ui/DocumentFindModal";
import { DocumentNotificationStrip } from "../../ui/DocumentNotificationStrip";
import { ItemSearchModal } from "../../ui/ItemSearchModal";
import { LineGridContextMenu, type LineGridCtxAction } from "../../ui/LineGridContextMenu";
import { LiveClock } from "../../ui/LiveClock";
import { SapAutocompleteInput } from "../../ui/SapAutocompleteInput";
import type { DocumentRegistryEntry, HeaderField } from "./documentTypes";
import { fetchItemByCode } from "../sales/shared/itemMasterApi";
import { SapSalesRightPanel } from "../sales/shared/SapSalesRightPanel";
import {
  apiLineToFormset,
  buildCreateBody,
  buildLinePostJson,
  buildPatchBody,
  computeLineTotalString,
  emptyFormsetRow,
  FORMSET_ROWS,
  formsetClearRowInPlace,
  formsetDeleteShiftUp,
  formsetDuplicateBelow,
  formsetInsertEmptyAbove,
  formsetInsertEmptyBelow,
  formsetNonEmptyRowsToTsv,
  formsetPad,
  formsetRefreshLineTotals,
  formsetRowIsEmpty,
  formsetRowToTsv,
  lineNetNoDisc,
  linePatchKeySet,
  parseTsvLineToFormsetRow,
  todayISO,
  toInputDate,
  type FormsetRow,
  type Row,
} from "./formset";

function lineColClass(key: string): string {
  const m: Record<string, string> = {
    ItemCode: "col-item",
    Dscription: "col-desc",
    Quantity: "col-qty",
    Price: "col-price",
    DiscPrcnt: "col-disc",
    LineTotal: "col-total",
    WhsCode: "col-whs",
    LineStatus: "col-disc",
    PlannedQty: "col-qty",
    IssuedQty: "col-qty",
    BaseType: "col-price",
    BaseEntry: "col-price",
    BaseLine: "col-price",
  };
  return m[key] ?? "";
}

type ListPage = { items: Row[]; limit: number; offset: number };

export type SapDocumentCrudProps = {
  def: DocumentRegistryEntry;
  workspaceTabId: string;
};

function rowPrimaryKey(row: Row, def: DocumentRegistryEntry): string | number | null {
  const k = def.pkKeys[0];
  if (!k) return null;
  const v = row[k];
  if (v == null || String(v).trim() === "") return null;
  const hf = def.headerFields.find((h) => h.key === k);
  if (hf?.kind === "number") return Number(v);
  return String(v);
}

/** SAP-style document window (Contents grid, footer, find) — shared by Sales / Purchase / Production. */
export function SapDocumentCrud({ def, workspaceTabId }: SapDocumentCrudProps) {
  const { registerTabActions } = useWorkspace();
  const canUpdate = import.meta.env.VITE_INVENTORY_READONLY === "true" ? false : true;

  const [rows, setRows] = useState<Row[]>([]);
  const [form, setForm] = useState<Row>({});
  const [orig, setOrig] = useState<Row | null>(null);
  const [mode, setMode] = useState<"new" | "edit">("new");
  const [headerSel, setHeaderSel] = useState<number | null>(null);
  const [formset, setFormset] = useState<FormsetRow[]>(() => formsetPad([]));
  const [linesSnapshot, setLinesSnapshot] = useState<Map<number, Row>>(() => new Map());
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [itemSearchOpen, setItemSearchOpen] = useState(false);
  const [itemSearchRow, setItemSearchRow] = useState<number | null>(null);
  const [bpSearchOpen, setBpSearchOpen] = useState(false);
  const [selectedFormsetRow, setSelectedFormsetRow] = useState<number | null>(null);
  const [findModalOpen, setFindModalOpen] = useState(false);
  const [findFilter, setFindFilter] = useState("");
  const [findRows, setFindRows] = useState<Row[]>([]);
  const [findBusy, setFindBusy] = useState(false);
  const [findErr, setFindErr] = useState("");
  const [lineCtx, setLineCtx] = useState<{ x: number; y: number; row: number } | null>(null);
  const listOffset = useRef(0);
  const itemFetchGen = useRef(0);

  const loadList = useCallback(
    async (searchPrefix?: string) => {
      setBusy(true);
      setErr("");
      try {
        const q = new URLSearchParams({ limit: "100", offset: String(listOffset.current) });
        if (searchPrefix != null && searchPrefix !== "") q.set("q", searchPrefix);
        const data = await apiFetch<ListPage>(`${def.listPath}?${q}`);
        setRows(data.items || []);
        setMsg(`Loaded ${data.items?.length ?? 0} row(s).`);
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Load failed");
      } finally {
        setBusy(false);
      }
    },
    [def],
  );

  const loadFindRows = useCallback(
    async (searchPrefix: string) => {
      setFindBusy(true);
      setFindErr("");
      try {
        const q = new URLSearchParams({ limit: "100", offset: "0" });
        const t = searchPrefix.trim();
        if (t !== "") q.set("q", t);
        const data = await apiFetch<ListPage>(`${def.listPath}?${q}`);
        setFindRows(data.items || []);
      } catch (e) {
        setFindErr(e instanceof Error ? e.message : "Load failed");
        setFindRows([]);
      } finally {
        setFindBusy(false);
      }
    },
    [def.listPath],
  );

  useEffect(() => {
    if (!findModalOpen) return;
    const h = setTimeout(() => {
      void loadFindRows(findFilter);
    }, 200);
    return () => clearTimeout(h);
  }, [findModalOpen, findFilter, loadFindRows]);

  const applyLinesToFormset = useCallback(
    (items: Row[]) => {
      const mapped = items.map((r) => apiLineToFormset(r, def.lines.editKeys));
      setFormset(formsetPad(mapped));
      const m = new Map<number, Row>();
      for (const r of items) {
        const ln = Number(r.LineNum);
        if (Number.isFinite(ln)) m.set(ln, { ...r });
      }
      setLinesSnapshot(m);
    },
    [def.lines.editKeys],
  );

  const loadLines = useCallback(
    async (parentPk: string | number) => {
      setBusy(true);
      setErr("");
      try {
        const data = await apiFetch<ListPage>(`${def.lines.listPath(parentPk)}`);
        applyLinesToFormset(data.items || []);
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Lines load failed");
        setFormset(formsetPad([]));
        setLinesSnapshot(new Map());
      } finally {
        setBusy(false);
      }
    },
    [def.lines, applyLinesToFormset],
  );

  useEffect(() => {
    setForm({});
    setOrig(null);
    setMode("new");
    setHeaderSel(null);
    setFormset(formsetPad([]));
    setLinesSnapshot(new Map());
    setRows([]);
    setMsg("Use Find on the toolbar to open the list, or start a New document.");
  }, [def.id]);

  const applyRow = useCallback(
    (r: Row, idx: number) => {
      const next: Row = { ...r };
      for (const h of def.headerFields) {
        if (h.kind === "date") next[h.key] = toInputDate(r[h.key]);
      }
      setForm(next);
      setOrig({ ...r });
      setMode("edit");
      setHeaderSel(idx >= 0 ? idx : null);
      const pk = rowPrimaryKey(next, def);
      if (pk != null) {
        void loadLines(pk);
      } else {
        setFormset(formsetPad([]));
        setLinesSnapshot(new Map());
      }
    },
    [def, loadLines],
  );

  const onAdd = useCallback(() => {
    const blank: Row = {};
    for (const h of def.headerFields) {
      blank[h.key] = h.key === "DocDate" || h.key === "DocDueDate" || h.key === "TaxDate" || h.key === "PostDate" ? todayISO() : "";
    }
    if (def.headerFields.some((h) => h.key === "DocStatus")) blank.DocStatus = "O";
    if (def.headerFields.some((h) => h.key === "Status")) blank.Status = "P";
    if (def.headerFields.some((h) => h.key === "TreeType")) blank.TreeType = "P";
    if (def.headerFields.some((h) => h.key === "DocTotal")) blank.DocTotal = "0";
    if (def.headerFields.some((h) => h.key === "VatSum")) blank.VatSum = "0";
    if (def.headerFields.some((h) => h.key === "DiscSum")) blank.DiscSum = "0";
    if (def.headerFields.some((h) => h.key === "DocCur")) blank.DocCur = "";
    if (def.headerFields.some((h) => h.key === "Quantity")) blank.Quantity = "1";
    if (def.headerFields.some((h) => h.key === "PlannedQty")) blank.PlannedQty = "0";
    if (def.headerFields.some((h) => h.key === "CmpltQty")) blank.CmpltQty = "0";
    setForm(blank);
    setOrig(null);
    setMode("new");
    setHeaderSel(null);
    setFormset(formsetPad([]));
    setLinesSnapshot(new Map());
    setMsg("New document — fill lines in Contents (10 rows); empty rows are not saved.");
  }, [def.headerFields]);

  const runDocumentFind = useCallback(() => {
    const pk = def.pkKeys[0];
    const raw = pk ? String(form[pk] ?? "").trim() : "";
    setFindFilter(raw);
    setFindModalOpen(true);
  }, [def.pkKeys, form]);

  const onFindPick = useCallback(
    (r: Record<string, unknown>, idx: number) => {
      const row = r as Row;
      setFindModalOpen(false);
      setFindErr("");
      setRows([...findRows]);
      applyRow(row, idx);
      setMsg("Document loaded.");
    },
    [findRows, applyRow],
  );

  const navDocFirst = useCallback(() => {
    if (rows.length) applyRow(rows[0], 0);
  }, [rows, applyRow]);
  const navDocPrev = useCallback(() => {
    if (headerSel != null && headerSel > 0) applyRow(rows[headerSel - 1], headerSel - 1);
  }, [headerSel, rows, applyRow]);
  const navDocNext = useCallback(() => {
    if (headerSel != null && headerSel < rows.length - 1) applyRow(rows[headerSel + 1], headerSel + 1);
  }, [headerSel, rows, applyRow]);
  const navDocLast = useCallback(() => {
    if (rows.length) applyRow(rows[rows.length - 1], rows.length - 1);
  }, [rows, applyRow]);

  useEffect(() => {
    registerTabActions(workspaceTabId, {
      find: () => void runDocumentFind(),
      newDoc: () => onAdd(),
      first: () => void navDocFirst(),
      prev: () => void navDocPrev(),
      next: () => void navDocNext(),
      last: () => void navDocLast(),
      print: () => {
        window.print();
      },
    });
    return () => registerTabActions(workspaceTabId, null);
  }, [workspaceTabId, registerTabActions, runDocumentFind, onAdd, navDocFirst, navDocPrev, navDocNext, navDocLast]);

  function setField(key: string, v: string) {
    setForm((f) => ({ ...f, [key]: v }));
  }

  function patchFormsetRow(i: number, patch: Partial<FormsetRow>) {
    setFormset((prev) => {
      const next = [...prev];
      const merged = { ...next[i], ...patch };
      if (def.lines.editKeys.includes("LineTotal")) {
        merged.LineTotal = def.lines.editKeys.includes("DiscPrcnt")
          ? computeLineTotalString(merged.Quantity, merged.Price, merged.DiscPrcnt)
          : lineNetNoDisc(merged.Quantity, merged.Price);
      }
      next[i] = merged;
      return next;
    });
  }

  function onLineGridBodyContextMenu(e: React.MouseEvent<HTMLTableSectionElement>) {
    const tr = (e.target as HTMLElement).closest("tr");
    if (!tr || !e.currentTarget.contains(tr)) return;
    const idxAttr = tr.getAttribute("data-line-idx");
    if (idxAttr == null) return;
    const row = Number(idxAttr);
    if (!Number.isFinite(row) || row < 0 || row >= FORMSET_ROWS) return;
    e.preventDefault();
    setSelectedFormsetRow(row);
    setLineCtx({ x: e.clientX, y: e.clientY, row });
  }

  async function clipboardWrite(text: string) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      /* secured context / permission */
    }
  }

  function handleLineGridMenuAction(action: LineGridCtxAction) {
    const rIdx = lineCtx?.row;
    setLineCtx(null);
    if (rIdx == null) return;
    const readOnly = !canUpdate;
    if (readOnly && action !== "copy" && action !== "copyTable") return;

    const ek = def.lines.editKeys;
    const applyRows = (next: FormsetRow[]) => {
      setFormset(formsetPad(next));
    };

    switch (action) {
      case "copy": {
        const r = formset[rIdx];
        if (r) void clipboardWrite(formsetRowToTsv(r));
        break;
      }
      case "copyTable":
        void clipboardWrite(formsetNonEmptyRowsToTsv(formset, ek));
        break;
      case "cut": {
        const r = formset[rIdx];
        if (r) void clipboardWrite(formsetRowToTsv(r));
        applyRows(formsetDeleteShiftUp(formset, rIdx, ek));
        setSelectedFormsetRow(rIdx);
        break;
      }
      case "paste": {
        void (async () => {
          try {
            const t = await navigator.clipboard.readText();
            const first = t.replace(/\r/g, "").split("\n").find((ln) => ln.trim() !== "") ?? "";
            const parsed = parseTsvLineToFormsetRow(first);
            if (!parsed) return;
            setFormset((prev) => {
              const next = formsetPad(prev);
              next[rIdx] = parsed;
              return formsetRefreshLineTotals(next, def.lines.editKeys);
            });
            setSelectedFormsetRow(rIdx);
          } catch {
            /* clipboard read denied */
          }
        })();
        break;
      }
      case "delete":
        applyRows(formsetClearRowInPlace(formset, rIdx, ek));
        break;
      case "addRow":
      case "addBelow":
        applyRows(formsetInsertEmptyBelow(formset, rIdx, ek));
        setSelectedFormsetRow(Math.min(rIdx + 1, FORMSET_ROWS - 1));
        break;
      case "addAbove":
        applyRows(formsetInsertEmptyAbove(formset, rIdx, ek));
        setSelectedFormsetRow(rIdx);
        break;
      case "deleteRow":
        applyRows(formsetDeleteShiftUp(formset, rIdx, ek));
        setSelectedFormsetRow(rIdx);
        break;
      case "removeAbove":
        if (rIdx > 0) {
          applyRows(formsetDeleteShiftUp(formset, rIdx - 1, ek));
          setSelectedFormsetRow(rIdx - 1);
        }
        break;
      case "removeBelow":
        if (rIdx < FORMSET_ROWS - 1) {
          applyRows(formsetDeleteShiftUp(formset, rIdx + 1, ek));
          setSelectedFormsetRow(rIdx);
        }
        break;
      case "duplicateRow":
        applyRows(formsetDuplicateBelow(formset, rIdx, ek));
        setSelectedFormsetRow(Math.min(rIdx + 1, FORMSET_ROWS - 1));
        break;
      default:
        break;
    }
  }

  async function applyPartnerToHeader(cardCode: string) {
    const codeKey = def.partnerPickerFieldKey ?? "CardCode";
    const nameKey = def.partnerNameFieldKey ?? "CardName";
    const curKey = def.partnerCurrencyFieldKey ?? "DocCur";
    const code = String(cardCode ?? "").trim();
    if (!code) {
      setForm((f) => ({ ...f, [codeKey]: "", [nameKey]: "" }));
      return;
    }
    try {
      const p = await fetchBusinessPartner(code);
      setForm((f) => ({
        ...f,
        [codeKey]: String(p.CardCode ?? code),
        [nameKey]: String(p.CardName ?? ""),
        ...(def.headerFields.some((h) => h.key === curKey) && p.Currency != null && String(p.Currency).trim() !== ""
          ? { [curKey]: String(p.Currency) }
          : {}),
      }));
    } catch {
      /* manual code */
    }
  }

  async function applyItemMasterToRow(rowIndex: number, itemCode: string) {
    const code = itemCode.trim();
    const gen = ++itemFetchGen.current;
    if (!code) {
      setFormset((prev) => {
        const next = [...prev];
        const ln = next[rowIndex].__lineNum;
        const cleared: FormsetRow = { ...emptyFormsetRow(), __lineNum: ln };
        if (def.lines.editKeys.includes("LineTotal")) {
          cleared.LineTotal = def.lines.editKeys.includes("DiscPrcnt")
            ? computeLineTotalString(cleared.Quantity, cleared.Price, cleared.DiscPrcnt)
            : lineNetNoDisc(cleared.Quantity, cleared.Price);
        }
        next[rowIndex] = cleared;
        return next;
      });
      return;
    }
    try {
      const item = await fetchItemByCode(code);
      if (itemFetchGen.current !== gen) return;
      const wh = String(item.DfltWH ?? "").trim() || "01";
      const patch: Partial<FormsetRow> = {
        ItemCode: String(item.ItemCode ?? code),
        WhsCode: wh,
      };
      if (def.lines.editKeys.includes("Dscription")) {
        patch.Dscription = String(item.ItemName ?? "");
      }
      patchFormsetRow(rowIndex, patch);
    } catch {
      /* manual / unknown item — keep typed code */
    }
  }

  async function postFilledLines(parentPk: string | number, draft: FormsetRow[]) {
    const toSave = draft.filter((r) => !formsetRowIsEmpty(r, def.lines.editKeys));
    let ln = 1;
    for (const r of toSave) {
      const json = buildLinePostJson(def, parentPk, ln, r);
      json.LineNum = ln;
      await apiFetch(def.lines.postPath, { method: "POST", json });
      ln += 1;
    }
  }

  async function syncLinesOnEdit(parentPk: string | number, draft: FormsetRow[]) {
    const snap = linesSnapshot;
    const patchKeys = linePatchKeySet(def);
    const deleted = new Set<number>();
    for (const r of draft) {
      if (r.__lineNum != null && formsetRowIsEmpty(r, def.lines.editKeys)) deleted.add(r.__lineNum);
    }
    let maxLn = 0;
    snap.forEach((row, num) => {
      if (deleted.has(num)) return;
      maxLn = Math.max(maxLn, num);
      const n = Number(row.LineNum);
      if (Number.isFinite(n)) maxLn = Math.max(maxLn, n);
    });
    for (const r of draft) {
      if (r.__lineNum != null && !formsetRowIsEmpty(r, def.lines.editKeys) && !deleted.has(r.__lineNum)) {
        maxLn = Math.max(maxLn, r.__lineNum);
      }
    }
    for (const r of draft) {
      if (r.__lineNum != null && formsetRowIsEmpty(r, def.lines.editKeys)) {
        await apiFetch(def.lines.detailPath(parentPk, r.__lineNum), { method: "DELETE" });
      }
    }
    for (const r of draft) {
      const ln = r.__lineNum;
      if (ln == null || formsetRowIsEmpty(r, def.lines.editKeys)) continue;
      const orig = snap.get(ln);
      if (!orig) continue;
      const patch: Row = {};
      for (const k of def.lines.editKeys) {
        if (!patchKeys.has(k)) continue;
        const fk = k as keyof FormsetRow;
        const nv = String(r[fk] ?? "");
        const ov = orig[k] != null ? String(orig[k]) : "";
        if (nv !== ov) patch[k] = nv;
      }
      if (Object.keys(patch).length) {
        await apiFetch(def.lines.detailPath(parentPk, ln), { method: "PATCH", json: patch });
      }
    }
    let nextLn = maxLn + 1;
    for (const r of draft) {
      if (r.__lineNum != null || formsetRowIsEmpty(r, def.lines.editKeys)) continue;
      const json = buildLinePostJson(def, parentPk, nextLn, r);
      json.LineNum = nextLn;
      await apiFetch(def.lines.postPath, { method: "POST", json });
      nextLn += 1;
    }
  }

  async function onSaveHeader() {
    if (!canUpdate) return;
    setErr("");
    setBusy(true);
    try {
      if (mode === "new") {
        const body = buildCreateBody(def, form);
        const created = await apiFetch<Row>(`${def.listPath}`, { method: "POST", json: body });
        const pk = rowPrimaryKey(created, def);
        if (pk == null) throw new Error("No primary key in create response");
        await postFilledLines(pk, formset);
        setMsg("Created with lines.");
        await loadList();
        applyRow(created, -1);
      } else {
        const body = buildPatchBody(def, form, orig);
        if (Object.keys(body).length) {
          const url = def.detailPath(form);
          await apiFetch(url, { method: "PATCH", json: body });
        }
        const pk = rowPrimaryKey(form, def);
        if (pk != null) await syncLinesOnEdit(pk, formset);
        setMsg("Updated.");
        const url = def.detailPath(form);
        const data = await apiFetch<Row>(url);
        await loadList();
        applyRow(data, -1);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  function renderField(h: HeaderField) {
    const v = form[h.key] != null ? String(form[h.key]) : "";
    const ro = !canUpdate || h.readonly || (h.pk && mode === "edit");
    const cls = "field-input field-input-grow" + (ro ? " readonly" : "");
    if (h.kind === "date") {
      return <input className={cls} readOnly={ro} type="date" value={v} onChange={(e) => setField(h.key, e.target.value)} />;
    }
    return <input className={cls} readOnly={ro} type={h.kind === "number" ? "number" : "text"} value={v} onChange={(e) => setField(h.key, e.target.value)} />;
  }

  function renderHeaderField(h: HeaderField) {
    const partnerKey = def.partnerPickerFieldKey ?? "CardCode";
    if (partnerKey != null && h.key === partnerKey) {
      const v = form[partnerKey] != null ? String(form[partnerKey]) : "";
      const ro = !canUpdate || h.readonly || (h.pk && mode === "edit");
      return (
        <SapAutocompleteInput
          wrapperClassName="sap-input-autocomplete--grow"
          inputClassName={"field-input field-input-grow" + (ro ? " readonly" : "")}
          type="text"
          value={v}
          readOnly={ro}
          onChange={(e) => setField(partnerKey, e.target.value)}
          onBlur={(e) => void applyPartnerToHeader(e.target.value)}
          onOpenList={() => {
            if (!ro) setBpSearchOpen(true);
          }}
          listButtonTitle={def.listButtonTitleBp ?? "Business partner list"}
          aria-label={h.label}
        />
      );
    }
    return renderField(h);
  }

  const footerLeftKeys = def.footerLeftKeys ?? ["SlpCode", "OwnerCode", "Comments"];
  const footerTotalsKeys = def.footerTotalsKeys ?? ["DiscSum", "VatSum", "DocTotal"];
  const footerKeySet = useMemo(() => new Set([...footerLeftKeys, ...footerTotalsKeys]), [footerLeftKeys, footerTotalsKeys]);
  const headerForGrid = useMemo(() => def.headerFields.filter((h) => !footerKeySet.has(h.key)), [def.headerFields, footerKeySet]);
  const leftFields = headerForGrid.filter((_, i) => i % 2 === 0);
  const rightFields = headerForGrid.filter((_, i) => i % 2 === 1);
  const docCur = form.DocCur != null ? String(form.DocCur) : "";
  const showCurHint = def.showDocCurHint !== false && docCur !== "";
  const lineDataCols = useMemo(() => def.lines.columns.filter((c) => c.key !== "LineNum"), [def.lines.columns]);
  const docRootClass = def.docRootClassName ?? "sap-sales-doc";
  const windowClass = def.windowClassName ?? "sap-window-sales";

  function renderLineCell(colKey: string, i: number, r: FormsetRow): ReactNode {
    const editable = def.lines.editKeys.includes(colKey);
    const v = String((r as unknown as Record<string, string>)[colKey] ?? "");
    const qtyCls = colKey === "Quantity" || colKey === "PlannedQty" || colKey === "IssuedQty" ? " cell-input-qty" : "";
    if (colKey === "ItemCode") {
      return (
        <SapAutocompleteInput
          wrapperClassName="sap-input-autocomplete--cell"
          inputClassName="cell-input"
          value={r.ItemCode}
          onChange={(e) => patchFormsetRow(i, { ItemCode: e.target.value })}
          onBlur={(e) => void applyItemMasterToRow(i, e.target.value)}
          onOpenList={() => {
            setItemSearchRow(i);
            setItemSearchOpen(true);
          }}
          listButtonTitle="Item list"
          aria-label={`Item row ${i + 1}`}
        />
      );
    }
    if (colKey === "LineTotal") {
      const ro = !editable;
      return (
        <input
          className={"cell-input" + (ro ? " cell-input-readonly" : "")}
          readOnly={ro}
          tabIndex={ro ? -1 : 0}
          value={v}
          onChange={ro ? undefined : (e) => patchFormsetRow(i, { LineTotal: e.target.value })}
          inputMode="decimal"
        />
      );
    }
    return (
      <input
        className={"cell-input" + qtyCls}
        value={v}
        readOnly={!editable}
        tabIndex={!editable ? -1 : 0}
        onChange={editable ? (e) => patchFormsetRow(i, { [colKey]: e.target.value } as Partial<FormsetRow>) : undefined}
        inputMode={colKey === "Quantity" || colKey === "Price" || colKey === "DiscPrcnt" || colKey === "PlannedQty" || colKey === "IssuedQty" ? "decimal" : undefined}
      />
    );
  }

  return (
    <div className={`sap-doc-root ${docRootClass}`}>
      <div className="sap-doc-layout">
        <div className={`sap-window ${windowClass} ez-doc-window`}>
          <div className="ez-doc-window-scroll">
          <div className="sap-titlebar">
            <span>{def.title}</span>
            <div className="titlebar-btns">
              <span className="tb-btn-win">−</span>
              <span className="tb-btn-win">□</span>
              <span className="tb-btn-win">✕</span>
            </div>
          </div>

          {!canUpdate ? (
            <div className="sap-readonly-banner">View only — updates are disabled (set VITE_INVENTORY_READONLY≠true to edit).</div>
          ) : null}

          <div className="sap-header">
            <div className="header-grid">
              <div>
                {leftFields.map((h) => (
                  <div key={h.key} className="field-row">
                    <span className="field-label">{h.label}</span>
                    {renderHeaderField(h)}
                  </div>
                ))}
              </div>
              <div>
                {rightFields.map((h) => (
                  <div key={h.key} className="field-row">
                    <span className="field-label">{h.label}</span>
                    {renderHeaderField(h)}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="sap-window-body">
            <div className="tab-panel sap2-contents-panel active">
              <div className="contents-controls">
                <div className="contents-controls-left">
                  <span className="field-label field-label-tight">Item/Service Type</span>
                  <select className="field-select field-select-100" defaultValue="Item" aria-label="Item or Service">
                    <option value="Item">Item</option>
                    <option value="Service">Service</option>
                  </select>
                  <span className="combo-arrow">▼</span>
                </div>
                <div className="contents-controls-spacer" />
                <div className="contents-controls-right">
                  <span className="field-label field-label-tight">Summary Type</span>
                  <select className="field-select field-select-110" defaultValue="No Summary" aria-label="Summary type">
                    <option>No Summary</option>
                    <option>By Items</option>
                    <option>By Documents</option>
                  </select>
                  <span className="combo-arrow">▼</span>
                </div>
              </div>
              <div className="grid-wrap sap2-line-grid">
                <table className="sap-table sap2-line-table">
                  <thead>
                    <tr>
                      <th className="col-num">#</th>
                      {lineDataCols.map((c) => (
                        <th key={c.key} className={lineColClass(c.key)}>
                          {c.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody onContextMenu={onLineGridBodyContextMenu}>
                    {formset.map((r, i) => (
                      <tr
                        key={i}
                        data-line-idx={i}
                        className={"sap-grid-row" + (selectedFormsetRow === i ? " formset-row-selected" : "")}
                        onClick={() => setSelectedFormsetRow(i)}
                      >
                        <td className="row-num">{i + 1}</td>
                        {lineDataCols.map((c) => (
                          <td key={c.key}>{renderLineCell(c.key, i, r)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="sap-footer">
                <div className="sap-footer-remarks">
                  {footerLeftKeys.map((key) => {
                    const hf = def.headerFields.find((h) => h.key === key);
                    if (!hf) return null;
                    if (hf.key === "Comments") {
                      return (
                        <div key={key} className="field-row" style={{ marginTop: 3, alignItems: "flex-start" }}>
                          <span className="field-label" style={{ paddingTop: 2 }}>
                            {hf.label}
                          </span>
                          <textarea
                            className="sap-footer-remarks-text"
                            readOnly={!canUpdate}
                            value={form[hf.key] != null ? String(form[hf.key]) : ""}
                            onChange={(e) => setField(hf.key, e.target.value)}
                          />
                        </div>
                      );
                    }
                    return (
                      <div key={key} className="field-row">
                        <span className="field-label">{hf.label}</span>
                        {renderField(hf)}
                      </div>
                    );
                  })}
                </div>
                <div>
                  <table className="totals-table">
                    <tbody>
                      {footerTotalsKeys.map((key, idx) => {
                        const hf = def.headerFields.find((h) => h.key === key);
                        if (!hf) return null;
                        const ro = !canUpdate || hf.readonly || key === "DocTotal" || key === "VatSum";
                        return (
                          <tr key={key}>
                            <td className="total-label">{hf.label}</td>
                            <td>
                              <input
                                className={"total-input" + (ro ? "" : " editable")}
                                readOnly={ro}
                                type="text"
                                value={form[key] != null ? String(form[key]) : ""}
                                onChange={ro ? undefined : (e) => setField(key, e.target.value)}
                              />
                            </td>
                            <td>{showCurHint && idx === 0 ? <span className="total-cur-hint">{docCur}</span> : null}</td>
                          </tr>
                        );
                      })}
                      {footerTotalsKeys.includes("DiscSum") ? (
                        <>
                          <tr>
                            <td className="total-label" />
                            <td>
                              <input className="total-input editable" readOnly={!canUpdate} type="text" placeholder="%" defaultValue="" />
                            </td>
                            <td className="total-pct-hint">%</td>
                          </tr>
                          <tr>
                            <td className="total-label total-label-compact">
                              <label className="rounding-label">
                                <input type="checkbox" disabled tabIndex={-1} aria-hidden />
                                Rounding
                              </label>
                            </td>
                            <td>
                              <input className="total-input" readOnly type="text" value={`${docCur ? `${docCur} ` : ""}0.00`} />
                            </td>
                            <td />
                          </tr>
                        </>
                      ) : null}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          </div>

          <div className="ez-doc-window-footer">
          <div className="sap-actionbar ez-doc-actionbar">
            <div className="ez-doc-actionbar__left">
              <button type="button" className="sap-btn ez-btn-primary-doc" onClick={() => void onSaveHeader()} disabled={busy || !canUpdate}>
                {mode === "new" ? "Add" : "Update"}
              </button>
              <button type="button" className="sap-btn" onClick={onAdd} disabled={busy}>
                Cancel
              </button>
            </div>
          </div>

          <div className="ez-doc-status-strip">
            <span className="ez-doc-status-segment ez-doc-status-segment--muted">{def.title}</span>
            <span className="ez-doc-status-segment ez-doc-status-segment--grow" />
            <span className="ez-doc-status-segment">
              {mode === "new"
                ? "Add mode"
                : (() => {
                    const pk = def.pkKeys[0];
                    const v = pk ? form[pk] : null;
                    return v != null && String(v).trim() !== "" ? `${pk} ${v}` : "Edit";
                  })()}
            </span>
            <LiveClock />
          </div>
          <DocumentNotificationStrip err={err} msg={msg} />
          </div>
        </div>

        <SapSalesRightPanel />
      </div>

      <LineGridContextMenu
        open={lineCtx != null}
        x={lineCtx?.x ?? 0}
        y={lineCtx?.y ?? 0}
        lineRowIndex={lineCtx?.row ?? 0}
        canMutate={canUpdate}
        onClose={() => setLineCtx(null)}
        onAction={handleLineGridMenuAction}
      />

      <DocumentFindModal
        open={findModalOpen}
        title={`${def.title} — find`}
        filterLabel={def.pkKeys.length ? `Filter (${def.pkKeys.join(" / ")})` : "Filter"}
        filterValue={findFilter}
        onFilterChange={setFindFilter}
        columns={def.listColumns}
        rows={findRows}
        busy={findBusy}
        err={findErr}
        onClose={() => setFindModalOpen(false)}
        onPick={(row, idx) => void onFindPick(row, idx)}
        onRefresh={() => void loadFindRows(findFilter)}
      />
      <ItemSearchModal
        open={itemSearchOpen}
        onClose={() => {
          setItemSearchOpen(false);
          setItemSearchRow(null);
        }}
        onPick={(row) => {
          if (itemSearchRow != null) {
            const i = itemSearchRow;
            void applyItemMasterToRow(i, String(row.ItemCode ?? ""));
          }
          setItemSearchOpen(false);
          setItemSearchRow(null);
        }}
      />
      <BpSearchModal
        open={bpSearchOpen}
        onClose={() => setBpSearchOpen(false)}
        onPick={(row) => {
          const codeKey = def.partnerPickerFieldKey ?? "CardCode";
          const nameKey = def.partnerNameFieldKey ?? "CardName";
          const curKey = def.partnerCurrencyFieldKey ?? "DocCur";
          const cc = String(row.CardCode ?? "");
          const nm = String(row.CardName ?? "");
          const cur = row.Currency != null ? String(row.Currency) : "";
          setForm((f) => ({
            ...f,
            [codeKey]: cc,
            [nameKey]: nm,
            ...(def.headerFields.some((h) => h.key === curKey) && cur.trim() !== "" ? { [curKey]: cur } : {}),
          }));
          setBpSearchOpen(false);
        }}
      />
    </div>
  );
}
