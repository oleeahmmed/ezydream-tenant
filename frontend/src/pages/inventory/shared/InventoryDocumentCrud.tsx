import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { apiFetch } from "../../../lib/apiFetch";
import { useWorkspace } from "../../../workspace/WorkspaceContext";
import { DocumentFindModal } from "../../../ui/DocumentFindModal";
import { DocumentNotificationStrip } from "../../../ui/DocumentNotificationStrip";
import { ItemSearchModal } from "../../../ui/ItemSearchModal";
import { LiveClock } from "../../../ui/LiveClock";
import { SapAutocompleteInput } from "../../../ui/SapAutocompleteInput";
import type { HeaderField, InvRegistryEntry } from "../registry";

type Row = Record<string, unknown>;

type ListPage = { items: Row[]; limit: number; offset: number };

const INV_API = "/api/inventory";

type ItemB1Tab = "general" | "purchasing" | "sales" | "stock" | "planning";

function toInputDate(v: unknown): string {
  if (v == null || v === "") return "";
  const s = String(v);
  if (s.length >= 10) return s.slice(0, 10);
  return s;
}

function toInputDt(v: unknown): string {
  if (v == null || v === "") return "";
  const s = String(v);
  if (s.includes("T")) return s.slice(0, 16);
  return s.replace(" ", "T").slice(0, 16);
}

function parseQty(v: unknown): number {
  const s = String(v ?? "").replace(/\s/g, "").replace(",", ".");
  const n = parseFloat(s);
  return Number.isFinite(n) ? n : 0;
}

function buildCreateBody(def: InvRegistryEntry, form: Row): Row {
  const o: Row = {};
  for (const k of def.createKeys) {
    if (form[k] === undefined || form[k] === "") continue;
    const f = def.headerFields.find((h) => h.key === k);
    if (f?.kind === "number") o[k] = Number(form[k]);
    else o[k] = form[k];
  }
  return o;
}

function buildPatchBody(def: InvRegistryEntry, form: Row, orig: Row | null): Row {
  if (!orig) return {};
  const o: Row = {};
  for (const k of def.patchKeys) {
    if (form[k] === undefined) continue;
    let a = form[k];
    let b = orig[k];
    if (def.headerFields.find((h) => h.key === k)?.kind === "number") {
      a = a === "" ? "" : Number(a);
      b = b === "" || b == null ? "" : Number(b);
    }
    if (String(a) !== String(b)) o[k] = a === "" ? "" : a;
  }
  return o;
}

/** Inventory document / master CRUD — layout aligned with sales documents. */
export function InventoryDocumentCrud({ def, workspaceTabId }: { def: InvRegistryEntry; workspaceTabId: string }) {
  const { registerTabActions, openInventoryModule } = useWorkspace();
  const formFirst = Boolean(def.formFirstListOnFind);
  const isItemMaster = def.id === "items";
  const canUpdate = import.meta.env.VITE_INVENTORY_READONLY === "true" ? false : true;

  const [rows, setRows] = useState<Row[]>([]);
  const [form, setForm] = useState<Row>({});
  const [orig, setOrig] = useState<Row | null>(null);
  const [mode, setMode] = useState<"new" | "edit">("new");
  const [headerSel, setHeaderSel] = useState<number | null>(null);
  const [lineRows, setLineRows] = useState<Row[]>([]);
  const [lineForm, setLineForm] = useState<Row>({});
  const [lineOrig, setLineOrig] = useState<Row | null>(null);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<"contents" | "lines">("contents");
  const [itemB1Tab, setItemB1Tab] = useState<ItemB1Tab>("general");
  const [whRows, setWhRows] = useState<Row[]>([]);
  const [itemSearchOpen, setItemSearchOpen] = useState(false);
  const [findModalOpen, setFindModalOpen] = useState(false);
  const [findFilter, setFindFilter] = useState("");
  const [findRows, setFindRows] = useState<Row[]>([]);
  const [findBusy, setFindBusy] = useState(false);
  const [findErr, setFindErr] = useState("");
  const listOffset = useRef(0);

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
        const q = new URLSearchParams({ limit: "100", offset: String(listOffset.current) });
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

  const loadLines = useCallback(
    async (docEntry: number) => {
      if (!def.lines) return;
      setBusy(true);
      setErr("");
      try {
        const data = await apiFetch<ListPage>(`${def.lines.listPath(docEntry)}&limit=200&offset=0`);
        setLineRows(data.items || []);
        setLineForm({});
        setLineOrig(null);
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Lines load failed");
      } finally {
        setBusy(false);
      }
    },
    [def],
  );

  const applyRow = useCallback(
    (r: Row, idx: number) => {
      const next: Row = { ...r };
      for (const h of def.headerFields) {
        if (h.kind === "date") next[h.key] = toInputDate(r[h.key]);
        if (h.kind === "datetime-local") next[h.key] = toInputDt(r[h.key]);
      }
      setForm(next);
      setOrig({ ...r });
      setMode("edit");
      setHeaderSel(idx >= 0 ? idx : null);
      if (def.lines && r.DocEntry != null) {
        void loadLines(Number(r.DocEntry));
        setTab("lines");
      } else {
        setLineRows([]);
        setLineForm({});
        setLineOrig(null);
      }
    },
    [def.headerFields, def.lines, loadLines],
  );

  const onAdd = useCallback(() => {
    const blank: Row = {};
    for (const h of def.headerFields) {
      blank[h.key] = "";
    }
    setForm(blank);
    setOrig(null);
    setMode("new");
    setHeaderSel(null);
    setLineRows([]);
    setLineForm({});
    setLineOrig(null);
    setTab("contents");
    setMsg(formFirst ? "Use Find on the toolbar to list records, then pick a row to load." : "Use Find on the toolbar to open the list, then pick a row to load.");
  }, [def.headerFields, formFirst]);

  const runDocumentFind = useCallback(() => {
    const pk = def.pkKeys[0];
    const raw = pk ? String(form[pk] ?? "").trim() : "";
    setFindFilter(raw);
    setFindModalOpen(true);
  }, [def.pkKeys, form]);

  const pickListRow = useCallback(
    async (r: Row, i: number) => {
      if (!formFirst) {
        applyRow(r, i);
        return;
      }
      setBusy(true);
      setErr("");
      try {
        const url = def.detailPath(r);
        const data = await apiFetch<Row>(url);
        applyRow(data, i);
        setMsg("Record loaded.");
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Load failed");
        applyRow(r, i);
      } finally {
        setBusy(false);
      }
    },
    [applyRow, def, formFirst],
  );

  const onFindPick = useCallback(
    async (r: Record<string, unknown>, idx: number) => {
      setFindModalOpen(false);
      setFindErr("");
      setRows([...findRows]);
      await pickListRow(r as Row, idx);
    },
    [findRows, pickListRow],
  );

  useEffect(() => {
    setForm({});
    setOrig(null);
    setMode("new");
    setHeaderSel(null);
    setLineRows([]);
    setTab("contents");
    setItemB1Tab("general");
    setWhRows([]);
    if (def.formFirstListOnFind) {
      const blank: Row = {};
      for (const h of def.headerFields) blank[h.key] = "";
      setForm(blank);
      setRows([]);
      setMsg(
        def.id === "items"
          ? "Item Master — use Find on the toolbar; type a prefix (e.g. 8) in the find window, then click a row to load."
          : "Use Find on the toolbar to open the list, then click a row to load.",
      );
    } else {
      setForm({});
      setRows([]);
      setMsg("Use Find on the toolbar to open the list, then click a row to load.");
    }
  }, [def.id, def.formFirstListOnFind, def.headerFields]);

  useEffect(() => {
    if (!isItemMaster || itemB1Tab !== "stock" || mode !== "edit") {
      if (!isItemMaster || itemB1Tab !== "stock") setWhRows([]);
      return;
    }
    const ic = String(form.ItemCode ?? "").trim();
    if (!ic) {
      setWhRows([]);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const q = new URLSearchParams({ item_code: ic, limit: "200", offset: "0" });
        const data = await apiFetch<ListPage>(`${INV_API}/item-warehouse-stock?${q}`);
        if (!cancelled) setWhRows(data.items || []);
      } catch {
        if (!cancelled) setWhRows([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isItemMaster, itemB1Tab, mode, form.ItemCode]);

  useEffect(() => {
    registerTabActions(workspaceTabId, {
      find: () => void runDocumentFind(),
      newDoc: () => onAdd(),
      first: () => {
        if (rows.length) applyRow(rows[0], 0);
      },
      prev: () => {
        if (headerSel != null && headerSel > 0) applyRow(rows[headerSel - 1], headerSel - 1);
      },
      next: () => {
        if (headerSel != null && headerSel < rows.length - 1) applyRow(rows[headerSel + 1], headerSel + 1);
      },
      last: () => {
        if (rows.length) applyRow(rows[rows.length - 1], rows.length - 1);
      },
      print: () => {
        window.print();
      },
    });
    return () => registerTabActions(workspaceTabId, null);
  }, [workspaceTabId, registerTabActions, runDocumentFind, onAdd, applyRow, rows, headerSel]);

  function setField(key: string, v: string) {
    setForm((f) => ({ ...f, [key]: v }));
  }

  async function onSaveHeader() {
    if (!canUpdate) return;
    setErr("");
    setBusy(true);
    try {
      if (mode === "new") {
        const body = buildCreateBody(def, form);
        await apiFetch(`${def.listPath}`, { method: "POST", json: body });
        setMsg("Created.");
        if (!formFirst) await loadList();
        onAdd();
      } else {
        const body = buildPatchBody(def, form, orig);
        if (Object.keys(body).length === 0) {
          setMsg("No changes to save.");
        } else {
          const url = def.detailPath(form);
          await apiFetch(url, { method: "PATCH", json: body });
          setMsg("Updated.");
          const data = await apiFetch<Row>(url);
          if (!formFirst) await loadList();
          applyRow(data, -1);
        }
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
    if (h.kind === "date" || h.kind === "datetime-local") {
      return (
        <input
          className={cls}
          readOnly={ro}
          type={h.kind === "date" ? "date" : "datetime-local"}
          value={v}
          onChange={(e) => setField(h.key, e.target.value)}
        />
      );
    }
    return <input className={cls} readOnly={ro} type={h.kind === "number" ? "number" : "text"} value={v} onChange={(e) => setField(h.key, e.target.value)} />;
  }

  function wrapItemGroupLink(h: HeaderField, node: ReactNode) {
    if (!isItemMaster || h.key !== "ItmsGrpCod") return node;
    const v = form.ItmsGrpCod != null ? String(form.ItmsGrpCod) : "";
    const ro = !canUpdate || h.readonly || (h.pk && mode === "edit");
    return (
      <SapAutocompleteInput
        wrapperClassName="sap-input-autocomplete--grow"
        inputClassName={"field-input field-input-grow" + (ro ? " readonly" : "")}
        type="number"
        value={v}
        readOnly={ro}
        onChange={(e) => setField("ItmsGrpCod", e.target.value)}
        onOpenList={() => openInventoryModule("item-groups", "Item Groups (OITB)", "/inventory/item-groups")}
        listButtonTitle="Open item groups"
        aria-label="Items group"
      />
    );
  }

  function wrapItemCodePicker(h: HeaderField, node: ReactNode) {
    if (!isItemMaster || h.key !== "ItemCode") return node;
    const v = form.ItemCode != null ? String(form.ItemCode) : "";
    const ro = !canUpdate || (h.pk && mode === "edit");
    return (
      <SapAutocompleteInput
        wrapperClassName="sap-input-autocomplete--grow"
        inputClassName={"field-input field-input-grow" + (ro ? " readonly" : "")}
        type="text"
        value={v}
        readOnly={ro}
        onChange={(e) => setField("ItemCode", e.target.value)}
        onOpenList={() => {
          if (!ro) setItemSearchOpen(true);
        }}
        listButtonTitle="Item list"
        aria-label="Item code"
      />
    );
  }

  const leftFields = def.headerFields.filter((_, i) => i % 2 === 0);
  const rightFields = def.headerFields.filter((_, i) => i % 2 === 1);

  function onLineRowClick(r: Row) {
    setLineForm({ ...r });
    setLineOrig({ ...r });
  }

  async function saveLine() {
    if (!def.lines || !lineOrig || form.DocEntry == null) return;
    const de = Number(form.DocEntry);
    const ln = Number(lineOrig.LineNum);
    const patch: Row = {};
    for (const k of def.lines.editKeys) {
      if (lineForm[k] === undefined) continue;
      if (String(lineForm[k]) !== String(lineOrig[k])) patch[k] = lineForm[k];
    }
    if (Object.keys(patch).length === 0) {
      setMsg("No line changes.");
    } else {
      setBusy(true);
      setErr("");
      try {
        await apiFetch(def.lines.detailPath(de, ln), { method: "PATCH", json: patch });
        setMsg("Line updated.");
        await loadLines(de);
      } catch (e) {
        setErr(e instanceof Error ? e.message : "Line save failed");
      } finally {
        setBusy(false);
      }
    }
  }

  async function addLine() {
    if (!def.lines || form.DocEntry == null) {
      setErr("Open a document (select row in Contents) so DocEntry is set.");
      return;
    }
    const de = Number(form.DocEntry);
    const maxLn = lineRows.reduce((m, r) => Math.max(m, Number(r.LineNum) || 0), 0);
    const nextLn = maxLn + 1;
    setBusy(true);
    setErr("");
    try {
      let json: Row = {};
      if (def.id === "str-req") {
        json = {
          DocEntry: de,
          LineNum: nextLn,
          ItemCode: "A00001",
          Quantity: "1",
          OpenQty: "1",
          Price: "0",
          FromWhsCod: "01",
          WhsCode: "01",
          LineStatus: "O",
          TargetType: -1,
          BaseRef: "",
        };
      } else if (def.id === "str") {
        json = { DocEntry: de, LineNum: nextLn, ItemCode: "A00001", Quantity: "1", FromWhsCod: "", WhsCode: "01", Price: "0" };
      } else if (def.id === "greceipt") {
        json = { DocEntry: de, LineNum: nextLn, ItemCode: "A00001", Quantity: "1", WhsCode: "01", Price: "0" };
      } else if (def.id === "gissue") {
        json = { DocEntry: de, LineNum: nextLn, ItemCode: "A00001", Quantity: "1", WhsCode: "01", Account: "", Price: "0" };
      } else if (def.id === "stktake") {
        json = { DocEntry: de, LineNum: nextLn, ItemCode: "A00001", WhsCode: "01", InQty: "0", OutQty: "0", Difference: "0", Price: "0" };
      }
      await apiFetch(def.lines.postPath, { method: "POST", json });
      setMsg(`Line ${nextLn} added — adjust item/WH in form and Update Line.`);
      await loadLines(de);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Add line failed");
    } finally {
      setBusy(false);
    }
  }

  async function deleteLine() {
    if (!def.lines || !lineOrig || form.DocEntry == null) return;
    const de = Number(form.DocEntry);
    const ln = Number(lineOrig.LineNum);
    if (!window.confirm(`Delete line ${ln}?`)) return;
    setBusy(true);
    setErr("");
    try {
      await apiFetch(def.lines.detailPath(de, ln), { method: "DELETE" });
      setMsg("Line removed.");
      setLineForm({});
      setLineOrig(null);
      await loadLines(de);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Line delete failed");
    } finally {
      setBusy(false);
    }
  }

  const lines = def.lines;

  const whTotals = useMemo(() => {
    let onHand = 0;
    let committed = 0;
    let ordered = 0;
    let avail = 0;
    for (const r of whRows) {
      const oh = parseQty(r.OnHand);
      const co = parseQty(r.IsCommited);
      const ord = parseQty(r.OrderQty);
      onHand += oh;
      committed += co;
      ordered += ord;
      avail += oh - co + ord;
    }
    return { onHand, committed, ordered, avail };
  }, [whRows]);

  const b1TabLabels: { id: ItemB1Tab; label: string }[] = [
    { id: "general", label: "General" },
    { id: "purchasing", label: "Purchasing Data" },
    { id: "sales", label: "Sales Data" },
    { id: "stock", label: "Stock Data" },
    { id: "planning", label: "Planning Data" },
  ];

  return (
    <div className="sap-doc-root">
      <div className="sap-window ez-doc-window">
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
                  {wrapItemCodePicker(h, wrapItemGroupLink(h, renderField(h)))}
                </div>
              ))}
            </div>
            <div>
              {rightFields.map((h) => (
                <div key={h.key} className="field-row">
                  <span className="field-label">{h.label}</span>
                  {wrapItemCodePicker(h, wrapItemGroupLink(h, renderField(h)))}
                </div>
              ))}
            </div>
          </div>
        </div>

        {isItemMaster ? (
          <>
            <div className="sap-tabs-bar b1-item-tabs">
              {b1TabLabels.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  className={`sap-tab${itemB1Tab === t.id ? " active" : ""}`}
                  onClick={() => setItemB1Tab(t.id)}
                >
                  {t.label}
                </button>
              ))}
            </div>
            {itemB1Tab === "general" ? (
              <div className="sap-b1-tab-stub">General — header fields are shown above (standard document layout).</div>
            ) : null}
            {itemB1Tab === "purchasing" || itemB1Tab === "sales" || itemB1Tab === "planning" ? (
              <div className="sap-b1-tab-stub">This tab is reserved (Purchasing / Sales / Planning).</div>
            ) : null}
            {itemB1Tab === "stock" ? (
              <div className="sap-stock-panel">
                <div className="sap-stock-note">Per-warehouse stock (OITW). Available = In Stock − Committed + Ordered.</div>
                <div className="grid-wrap">
                  <table className="sap-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Whse Code</th>
                        <th>Whse Name</th>
                        <th>Locked</th>
                        <th>In Stock</th>
                        <th>Committed</th>
                        <th>Ordered</th>
                        <th>Available</th>
                      </tr>
                    </thead>
                    <tbody>
                      {whRows.map((r, i) => {
                        const oh = parseQty(r.OnHand);
                        const co = parseQty(r.IsCommited);
                        const ord = parseQty(r.OrderQty);
                        const av = oh - co + ord;
                        return (
                          <tr key={`${r.WhsCode}-${i}`}>
                            <td>{i + 1}</td>
                            <td>{String(r.WhsCode ?? "")}</td>
                            <td />
                            <td>{String(r.Locked ?? "")}</td>
                            <td>{String(r.OnHand ?? "")}</td>
                            <td>{String(r.IsCommited ?? "")}</td>
                            <td>{String(r.OrderQty ?? "")}</td>
                            <td>{av.toFixed(3)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                    {whRows.length ? (
                      <tfoot>
                        <tr className="sap-table-totals">
                          <td colSpan={4} style={{ textAlign: "right", fontWeight: 700 }}>
                            Total
                          </td>
                          <td>{whTotals.onHand.toFixed(3)}</td>
                          <td>{whTotals.committed.toFixed(3)}</td>
                          <td>{whTotals.ordered.toFixed(3)}</td>
                          <td>{whTotals.avail.toFixed(3)}</td>
                        </tr>
                      </tfoot>
                    ) : null}
                  </table>
                </div>
              </div>
            ) : null}
          </>
        ) : (
          <>
            <div className="sap-tabs-bar">
              <button type="button" className={`sap-tab${tab === "contents" ? " active" : ""}`} onClick={() => setTab("contents")}>
                Contents
              </button>
              {lines ? (
                <button type="button" className={`sap-tab${tab === "lines" ? " active" : ""}`} onClick={() => setTab("lines")}>
                  Document Lines
                </button>
              ) : null}
            </div>

            <div className={`tab-panel${tab === "contents" ? " active" : ""}`}>
              {tab !== "contents" ? null : (
                <div className="sap-b1-tab-stub" style={{ borderTop: "1px solid #bbb", padding: "10px 12px" }}>
                  Use <strong>Find</strong> on the top toolbar to open the list{def.pkKeys[0] ? ` (optional prefix in ${def.pkKeys[0]})` : ""}, then click a row to load the record into this form.
                </div>
              )}
            </div>

            {lines ? (
              <div className={`tab-panel${tab === "lines" ? " active" : ""}`} style={{ borderTop: "1px solid #bbb" }}>
                <div style={{ padding: "6px 12px", fontSize: 11, fontWeight: 600 }}>Lines (select row to edit)</div>
                <div className="grid-wrap" style={{ maxHeight: 180 }}>
                  <table className="sap-table">
                    <thead>
                      <tr>
                        {lines.columns.map((c) => (
                          <th key={c.key}>{c.label}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {lineRows.map((r, i) => (
                        <tr
                          key={i}
                          className={lineOrig && Number(lineOrig.LineNum) === Number(r.LineNum) ? "selected" : ""}
                          style={{ cursor: "pointer" }}
                          onClick={() => onLineRowClick(r)}
                        >
                          {lines.columns.map((c) => (
                            <td key={c.key}>{r[c.key] != null ? String(r[c.key]) : ""}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {lineOrig ? (
                  <div className="sap-header" style={{ borderTop: "1px solid #ddd" }}>
                    <div className="header-grid">
                      {lines.editKeys.map((k) => (
                        <div key={k} className="field-row">
                          <span className="field-label">{k}</span>
                          <input
                            className="field-input field-input-grow"
                            value={lineForm[k] != null ? String(lineForm[k]) : ""}
                            onChange={(e) => setLineForm((f) => ({ ...f, [k]: e.target.value }))}
                          />
                        </div>
                      ))}
                    </div>
                    <div className="sap-actionbar" style={{ borderTop: "none" }}>
                      <button type="button" className="sap-btn primary" onClick={() => void saveLine()} disabled={busy}>
                        Update Line
                      </button>
                      <button type="button" className="sap-btn" onClick={() => void deleteLine()} disabled={busy}>
                        Remove Line
                      </button>
                    </div>
                  </div>
                ) : null}
                <div className="sap-actionbar">
                  <button type="button" className="sap-btn primary" onClick={() => void addLine()} disabled={busy}>
                    Add Line
                  </button>
                </div>
              </div>
            ) : null}
          </>
        )}

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
                  const k0 = def.pkKeys[0];
                  if (!k0) return "Edit";
                  const v = form[k0];
                  return v != null && String(v).trim() !== "" ? `${k0}: ${String(v)}` : "Edit";
                })()}
          </span>
          <LiveClock />
        </div>
        <DocumentNotificationStrip err={err} msg={msg} />
        </div>
      </div>
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
        onClose={() => setItemSearchOpen(false)}
        onPick={(row) => {
          setForm((f) => ({
            ...f,
            ItemCode: String(row.ItemCode ?? ""),
            ...(row.ItemName != null && row.ItemName !== undefined ? { ItemName: String(row.ItemName) } : {}),
          }));
          setItemSearchOpen(false);
        }}
      />
    </div>
  );
}
