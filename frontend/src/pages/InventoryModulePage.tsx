import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiFetch } from "../lib/apiFetch";
import { getInventoryModule, type HeaderField, type InvRegistryEntry } from "../inventory/registry";

type Row = Record<string, unknown>;

type ListPage = { items: Row[]; limit: number; offset: number };

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

/** SAP B1–style inventory CRUD (``frontend/ui/sap2.html`` layout). */
function InventoryCrud({ def }: { def: InvRegistryEntry }) {
  const nav = useNavigate();
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
  const listOffset = useRef(0);

  const loadList = useCallback(async () => {
    setBusy(true);
    setErr("");
    try {
      const q = new URLSearchParams({ limit: "100", offset: String(listOffset.current) });
      const data = await apiFetch<ListPage>(`${def.listPath}?${q}`);
      setRows(data.items || []);
      setMsg(`Loaded ${data.items?.length ?? 0} row(s).`);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Load failed");
    } finally {
      setBusy(false);
    }
  }, [def]);

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

  useEffect(() => {
    setForm({});
    setOrig(null);
    setMode("new");
    setHeaderSel(null);
    setLineRows([]);
    setTab("contents");
    void loadList();
  }, [def.id, loadList]);

  function setField(key: string, v: string) {
    setForm((f) => ({ ...f, [key]: v }));
  }

  function applyRow(r: Row, idx: number) {
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
  }

  function onAdd() {
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
    setMsg("New record — fill fields and press Add to save.");
  }

  async function onSaveHeader() {
    setErr("");
    setBusy(true);
    try {
      if (mode === "new") {
        const body = buildCreateBody(def, form);
        await apiFetch(`${def.listPath}`, { method: "POST", json: body });
        setMsg("Created.");
        await loadList();
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
          await loadList();
          applyRow(data, -1);
        }
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function onDeleteHeader() {
    if (mode !== "edit" || !orig) return;
    if (!window.confirm("Delete this record?")) return;
    setBusy(true);
    setErr("");
    try {
      await apiFetch(def.detailPath(form), { method: "DELETE" });
      setMsg("Deleted.");
      onAdd();
      await loadList();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setBusy(false);
    }
  }

  function renderField(h: HeaderField) {
    const v = form[h.key] != null ? String(form[h.key]) : "";
    const ro = h.readonly || (h.pk && mode === "edit");
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

  return (
    <div className="sap-doc-root">
      <div className="sap-window">
        <div className="sap-titlebar">
          <span>{def.title}</span>
          <div className="titlebar-btns">
            <span className="tb-btn-win">−</span>
            <span className="tb-btn-win">□</span>
            <span className="tb-btn-win">✕</span>
          </div>
        </div>

        <div className="sap-toolbar-doc">
          <button type="button" className="tb-tool-btn" onClick={() => void loadList()} disabled={busy}>
            🔍 Find
          </button>
          <button type="button" className="tb-tool-btn" onClick={onAdd}>
            📄 New
          </button>
          <button type="button" className="tb-tool-btn" onClick={() => nav("/")}>
            🏠 Home
          </button>
        </div>

        <div className="sap-header">
          <div className="header-grid">
            <div>
              {leftFields.map((h) => (
                <div key={h.key} className="field-row">
                  <span className="field-label">{h.label}</span>
                  {renderField(h)}
                </div>
              ))}
            </div>
            <div>
              {rightFields.map((h) => (
                <div key={h.key} className="field-row">
                  <span className="field-label">{h.label}</span>
                  {renderField(h)}
                </div>
              ))}
            </div>
          </div>
        </div>

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
          <div className="grid-wrap">
            <table className="sap-table">
              <thead>
                <tr>
                  {def.listColumns.map((c) => (
                    <th key={c.key}>{c.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={i} className={headerSel === i ? "selected" : ""} onClick={() => applyRow(r, i)} style={{ cursor: "pointer" }}>
                    {def.listColumns.map((c) => (
                      <td key={c.key}>{r[c.key] != null ? String(r[c.key]) : ""}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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

        <div className="sap-actionbar">
          <button type="button" className="sap-btn primary" onClick={() => void onSaveHeader()} disabled={busy}>
            {mode === "new" ? "Add" : "Update"}
          </button>
          <button type="button" className="sap-btn" onClick={onAdd} disabled={busy}>
            Cancel
          </button>
          <button type="button" className="sap-btn" onClick={() => void onDeleteHeader()} disabled={busy || mode === "new"}>
            Delete
          </button>
          <span className={err ? "sap-msg err" : "sap-msg"}>{err || msg}</span>
        </div>
      </div>
    </div>
  );
}

export default function InventoryModulePage() {
  const { moduleId } = useParams();
  const nav = useNavigate();
  const def = useMemo(() => getInventoryModule(moduleId), [moduleId]);
  useEffect(() => {
    if (!def) nav("/", { replace: true });
  }, [def, nav]);
  if (!def) return null;
  return <InventoryCrud key={def.id} def={def} />;
}
