import { useCallback, useEffect, useRef, useState } from "react";
import { apiFetch } from "../../../lib/apiFetch";
import { fetchBusinessPartner } from "../../../lib/businessPartnerApi";
import { useWorkspace } from "../../../workspace/WorkspaceContext";
import { BpSearchModal } from "../../../ui/BpSearchModal";
import { DocumentFindModal } from "../../../ui/DocumentFindModal";
import { DocumentNotificationStrip } from "../../../ui/DocumentNotificationStrip";
import { ItemSearchModal } from "../../../ui/ItemSearchModal";
import { LineGridContextMenu, type LineGridCtxAction } from "../../../ui/LineGridContextMenu";
import { LiveClock } from "../../../ui/LiveClock";
import { SapAutocompleteInput } from "../../../ui/SapAutocompleteInput";
import type { HeaderField, SalesRegistryEntry } from "../registry";
import { fetchItemByCode } from "./itemMasterApi";
import { SapSalesRightPanel } from "./SapSalesRightPanel";
import {
  HEADER_FIELDS_IN_FOOTER,
  LINE_PATCH_KEYS,
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
  formsetRowIsEmpty,
  formsetRowToTsv,
  parseTsvLineToFormsetRow,
  todayISO,
  toInputDate,
  type FormsetRow,
  type Row,
} from "./formset";

type ListPage = { items: Row[]; limit: number; offset: number };

export type SalesDocumentCrudProps = {
  def: SalesRegistryEntry;
  workspaceTabId: string;
};

/** Sales / A/R document UI — ``frontend/ui/sap2.html`` layout; lines from ``./formset``. */
export function SalesDocumentCrud({ def, workspaceTabId }: SalesDocumentCrudProps) {
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

  const applyLinesToFormset = useCallback((items: Row[]) => {
    const mapped = items.map(apiLineToFormset);
    setFormset(formsetPad(mapped));
    const m = new Map<number, Row>();
    for (const r of items) {
      const ln = Number(r.LineNum);
      if (Number.isFinite(ln)) m.set(ln, { ...r });
    }
    setLinesSnapshot(m);
  }, []);

  const loadLines = useCallback(
    async (docEntry: number) => {
      setBusy(true);
      setErr("");
      try {
        const data = await apiFetch<ListPage>(`${def.lines.listPath(docEntry)}`);
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
      if (r.DocEntry != null) {
        void loadLines(Number(r.DocEntry));
      } else {
        setFormset(formsetPad([]));
        setLinesSnapshot(new Map());
      }
    },
    [def.headerFields, loadLines],
  );

  const onAdd = useCallback(() => {
    const blank: Row = {};
    for (const h of def.headerFields) {
      blank[h.key] = h.key === "DocDate" || h.key === "DocDueDate" || h.key === "TaxDate" ? todayISO() : "";
    }
    if (def.headerFields.some((h) => h.key === "DocStatus")) blank.DocStatus = "O";
    blank.DocTotal = "0";
    blank.VatSum = "0";
    blank.DiscSum = "0";
    blank.DocCur = "";
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
      merged.LineTotal = computeLineTotalString(merged.Quantity, merged.Price, merged.DiscPrcnt);
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
        void clipboardWrite(formsetNonEmptyRowsToTsv(formset));
        break;
      case "cut": {
        const r = formset[rIdx];
        if (r) void clipboardWrite(formsetRowToTsv(r));
        applyRows(formsetDeleteShiftUp(formset, rIdx));
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
              return next;
            });
            setSelectedFormsetRow(rIdx);
          } catch {
            /* clipboard read denied */
          }
        })();
        break;
      }
      case "delete":
        applyRows(formsetClearRowInPlace(formset, rIdx));
        break;
      case "addRow":
      case "addBelow":
        applyRows(formsetInsertEmptyBelow(formset, rIdx));
        setSelectedFormsetRow(Math.min(rIdx + 1, FORMSET_ROWS - 1));
        break;
      case "addAbove":
        applyRows(formsetInsertEmptyAbove(formset, rIdx));
        setSelectedFormsetRow(rIdx);
        break;
      case "deleteRow":
        applyRows(formsetDeleteShiftUp(formset, rIdx));
        setSelectedFormsetRow(rIdx);
        break;
      case "removeAbove":
        if (rIdx > 0) {
          applyRows(formsetDeleteShiftUp(formset, rIdx - 1));
          setSelectedFormsetRow(rIdx - 1);
        }
        break;
      case "removeBelow":
        if (rIdx < FORMSET_ROWS - 1) {
          applyRows(formsetDeleteShiftUp(formset, rIdx + 1));
          setSelectedFormsetRow(rIdx);
        }
        break;
      case "duplicateRow":
        applyRows(formsetDuplicateBelow(formset, rIdx));
        setSelectedFormsetRow(Math.min(rIdx + 1, FORMSET_ROWS - 1));
        break;
      default:
        break;
    }
  }

  async function applyPartnerToHeader(cardCode: string) {
    const code = String(cardCode ?? "").trim();
    if (!code) {
      setForm((f) => ({ ...f, CardCode: "", CardName: "" }));
      return;
    }
    try {
      const p = await fetchBusinessPartner(code);
      setForm((f) => ({
        ...f,
        CardCode: String(p.CardCode ?? code),
        CardName: String(p.CardName ?? ""),
        ...(p.Currency != null && String(p.Currency).trim() !== "" ? { DocCur: String(p.Currency) } : {}),
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
        cleared.LineTotal = computeLineTotalString(cleared.Quantity, cleared.Price, cleared.DiscPrcnt);
        next[rowIndex] = cleared;
        return next;
      });
      return;
    }
    try {
      const item = await fetchItemByCode(code);
      if (itemFetchGen.current !== gen) return;
      const wh = String(item.DfltWH ?? "").trim() || "01";
      patchFormsetRow(rowIndex, {
        ItemCode: String(item.ItemCode ?? code),
        Dscription: String(item.ItemName ?? ""),
        WhsCode: wh,
      });
    } catch {
      /* manual / unknown item — keep typed code */
    }
  }

  async function postFilledLines(docEntry: number, draft: FormsetRow[]) {
    const toSave = draft.filter((r) => !formsetRowIsEmpty(r));
    let ln = 1;
    for (const r of toSave) {
      const json = buildLinePostJson(def, docEntry, ln, r);
      json.LineNum = ln;
      await apiFetch(def.lines.postPath, { method: "POST", json });
      ln += 1;
    }
  }

  async function syncLinesOnEdit(docEntry: number, draft: FormsetRow[]) {
    const snap = linesSnapshot;
    const deleted = new Set<number>();
    for (const r of draft) {
      if (r.__lineNum != null && formsetRowIsEmpty(r)) deleted.add(r.__lineNum);
    }
    let maxLn = 0;
    snap.forEach((row, num) => {
      if (deleted.has(num)) return;
      maxLn = Math.max(maxLn, num);
      const n = Number(row.LineNum);
      if (Number.isFinite(n)) maxLn = Math.max(maxLn, n);
    });
    for (const r of draft) {
      if (r.__lineNum != null && !formsetRowIsEmpty(r) && !deleted.has(r.__lineNum)) {
        maxLn = Math.max(maxLn, r.__lineNum);
      }
    }
    for (const r of draft) {
      if (r.__lineNum != null && formsetRowIsEmpty(r)) {
        await apiFetch(def.lines.detailPath(docEntry, r.__lineNum), { method: "DELETE" });
      }
    }
    for (const r of draft) {
      const ln = r.__lineNum;
      if (ln == null || formsetRowIsEmpty(r)) continue;
      const orig = snap.get(ln);
      if (!orig) continue;
      const patch: Row = {};
      for (const k of def.lines.editKeys) {
        if (!LINE_PATCH_KEYS.has(k)) continue;
        const fk = k as keyof FormsetRow;
        const nv = String(r[fk] ?? "");
        const ov = orig[k] != null ? String(orig[k]) : "";
        if (nv !== ov) patch[k] = nv;
      }
      if (Object.keys(patch).length) {
        await apiFetch(def.lines.detailPath(docEntry, ln), { method: "PATCH", json: patch });
      }
    }
    let nextLn = maxLn + 1;
    for (const r of draft) {
      if (r.__lineNum != null || formsetRowIsEmpty(r)) continue;
      const json = buildLinePostJson(def, docEntry, nextLn, r);
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
        const de = Number(created.DocEntry);
        if (!Number.isFinite(de)) throw new Error("No DocEntry in create response");
        await postFilledLines(de, formset);
        setMsg("Created with lines.");
        await loadList();
        applyRow(created, -1);
      } else {
        const body = buildPatchBody(def, form, orig);
        if (Object.keys(body).length) {
          const url = def.detailPath(form);
          await apiFetch(url, { method: "PATCH", json: body });
        }
        const de = Number(form.DocEntry);
        if (Number.isFinite(de)) await syncLinesOnEdit(de, formset);
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
    if (h.key === "CardCode") {
      const v = form.CardCode != null ? String(form.CardCode) : "";
      const ro = !canUpdate || h.readonly || (h.pk && mode === "edit");
      return (
        <SapAutocompleteInput
          wrapperClassName="sap-input-autocomplete--grow"
          inputClassName={"field-input field-input-grow" + (ro ? " readonly" : "")}
          type="text"
          value={v}
          readOnly={ro}
          onChange={(e) => setField("CardCode", e.target.value)}
          onBlur={(e) => void applyPartnerToHeader(e.target.value)}
          onOpenList={() => {
            if (!ro) setBpSearchOpen(true);
          }}
          listButtonTitle="Business partner list"
          aria-label="Customer code"
        />
      );
    }
    return renderField(h);
  }

  const headerForGrid = def.headerFields.filter((h) => !HEADER_FIELDS_IN_FOOTER.has(h.key));
  const leftFields = headerForGrid.filter((_, i) => i % 2 === 0);
  const rightFields = headerForGrid.filter((_, i) => i % 2 === 1);
  const docCur = form.DocCur != null ? String(form.DocCur) : "";

  return (
    <div className="sap-doc-root sap-sales-doc">
      <div className="sap-doc-layout">
        <div className={`sap-window sap-window-sales ez-doc-window`}>
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
                      <th className="col-item">Item No.</th>
                      <th className="col-desc">Item Description</th>
                      <th className="col-qty">Quantity</th>
                      <th className="col-price">Unit Price</th>
                      <th className="col-disc">Disc %</th>
                      <th className="col-total">Total (LC)</th>
                      <th className="col-whs">Whse</th>
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
                        <td>
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
                        </td>
                        <td>
                          <input
                            className="cell-input"
                            value={r.Dscription}
                            onChange={(e) => patchFormsetRow(i, { Dscription: e.target.value })}
                            placeholder="Item name"
                            aria-label={`Description row ${i + 1}`}
                          />
                        </td>
                        <td>
                          <input
                            className="cell-input cell-input-qty"
                            value={r.Quantity}
                            onChange={(e) => patchFormsetRow(i, { Quantity: e.target.value })}
                            inputMode="decimal"
                          />
                        </td>
                        <td>
                          <input
                            className="cell-input"
                            value={r.Price}
                            onChange={(e) => patchFormsetRow(i, { Price: e.target.value })}
                            inputMode="decimal"
                          />
                        </td>
                        <td>
                          <input className="cell-input" value={r.DiscPrcnt} onChange={(e) => patchFormsetRow(i, { DiscPrcnt: e.target.value })} inputMode="decimal" />
                        </td>
                        <td>
                          <input className="cell-input cell-input-readonly" readOnly tabIndex={-1} value={r.LineTotal} />
                        </td>
                        <td>
                          <input className="cell-input" value={r.WhsCode} onChange={(e) => patchFormsetRow(i, { WhsCode: e.target.value })} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="sap-footer">
                <div className="sap-footer-remarks">
                  <div className="field-row">
                    <span className="field-label">Sales Employee</span>
                    <input
                      className="field-input"
                      style={{ width: 160 }}
                      type="number"
                      readOnly={!canUpdate}
                      value={form.SlpCode != null ? String(form.SlpCode) : ""}
                      onChange={(e) => setField("SlpCode", e.target.value)}
                    />
                  </div>
                  <div className="field-row">
                    <span className="field-label">Owner</span>
                    <input
                      className="field-input"
                      style={{ width: 160 }}
                      type="text"
                      readOnly={!canUpdate}
                      value={form.OwnerCode != null ? String(form.OwnerCode) : ""}
                      onChange={(e) => setField("OwnerCode", e.target.value)}
                    />
                  </div>
                  <div className="field-row" style={{ marginTop: 3, alignItems: "flex-start" }}>
                    <span className="field-label" style={{ paddingTop: 2 }}>
                      Remarks
                    </span>
                    <textarea
                      className="sap-footer-remarks-text"
                      readOnly={!canUpdate}
                      value={form.Comments != null ? String(form.Comments) : ""}
                      onChange={(e) => setField("Comments", e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <table className="totals-table">
                    <tbody>
                      <tr>
                        <td className="total-label">Discount</td>
                        <td>
                          <input
                            className="total-input editable"
                            readOnly={!canUpdate}
                            type="text"
                            value={form.DiscSum != null ? String(form.DiscSum) : ""}
                            onChange={(e) => setField("DiscSum", e.target.value)}
                          />
                        </td>
                        <td>{docCur ? <span className="total-cur-hint">{docCur}</span> : null}</td>
                      </tr>
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
                      <tr>
                        <td className="total-label">Tax</td>
                        <td>
                          <input className="total-input" readOnly type="text" value={form.VatSum != null ? String(form.VatSum) : "0"} />
                        </td>
                        <td />
                      </tr>
                      <tr>
                        <td className="total-label">Total</td>
                        <td>
                          <input className="total-input" readOnly type="text" value={form.DocTotal != null ? String(form.DocTotal) : "0"} />
                        </td>
                        <td />
                      </tr>
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
              {mode === "new" ? "Add mode" : form.DocEntry != null && String(form.DocEntry).trim() !== "" ? `DocEntry ${form.DocEntry}` : "Edit"}
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
          const cc = String(row.CardCode ?? "");
          const nm = String(row.CardName ?? "");
          const cur = row.Currency != null ? String(row.Currency) : "";
          setForm((f) => ({
            ...f,
            CardCode: cc,
            CardName: nm,
            ...(cur.trim() !== "" ? { DocCur: cur } : {}),
          }));
          setBpSearchOpen(false);
        }}
      />
    </div>
  );
}
