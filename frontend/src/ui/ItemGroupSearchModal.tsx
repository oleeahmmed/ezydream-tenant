import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../lib/apiFetch";

type Row = Record<string, unknown>;

type ListPage = { items: Row[]; limit: number; offset: number };

const API = "/api/inventory/item-groups";

export type ItemGroupSearchModalProps = {
  open: boolean;
  onClose: () => void;
  onPick: (row: Row) => void;
};

/** Choose-from-list for OITB item groups (used from Item Master instead of opening another tab). */
export function ItemGroupSearchModal({ open, onClose, onPick }: ItemGroupSearchModalProps) {
  const [filter, setFilter] = useState("");
  const [rows, setRows] = useState<Row[]>([]);
  const [sel, setSel] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const load = useCallback(async (q: string) => {
    setBusy(true);
    setErr("");
    try {
      const sp = new URLSearchParams({ limit: "200", offset: "0" });
      if (q.trim()) sp.set("q", q.trim());
      const data = await apiFetch<ListPage>(`${API}?${sp}`);
      setRows(data.items || []);
      setSel(null);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Load failed");
      setRows([]);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    if (!open) return;
    void load("");
    setFilter("");
  }, [open, load]);

  useEffect(() => {
    if (!open) return;
    const t = setTimeout(() => void load(filter), 200);
    return () => clearTimeout(t);
  }, [filter, open, load]);

  function confirmPick() {
    if (sel == null || !rows[sel]) return;
    onPick(rows[sel]);
    onClose();
  }

  if (!open) return null;

  return (
    <div className="sap-modal-overlay" role="presentation" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="sap-modal-box sap-item-search-modal" role="dialog" aria-labelledby="item-group-search-title" onMouseDown={(e) => e.stopPropagation()}>
        <div className="sap-modal-head">
          <span id="item-group-search-title">Item Groups</span>
          <button type="button" className="sap-modal-close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        <div className="sap-modal-toolbar">
          <label className="sap-modal-label" htmlFor="item-group-search-filter">
            Filter
          </label>
          <input
            id="item-group-search-filter"
            className="field-input"
            style={{ width: 220 }}
            placeholder="Group code or name…"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void load(filter)}
          />
          <button type="button" className="sap-btn" onClick={() => void load(filter)} disabled={busy}>
            {busy ? "…" : "Refresh"}
          </button>
        </div>
        {err ? <div className="sap-modal-err">{err}</div> : null}
        <div className="sap-modal-body">
          <table className="sap-table item-search-table">
            <thead>
              <tr>
                <th>Group Code</th>
                <th>Group Name</th>
                <th>Canceled</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr
                  key={i}
                  className={sel === i ? "selected" : ""}
                  onClick={() => setSel(i)}
                  onDoubleClick={() => {
                    onPick(r);
                    onClose();
                  }}
                >
                  <td>{r.ItmsGrpCod != null ? String(r.ItmsGrpCod) : ""}</td>
                  <td>{r.ItmsGrpNam != null ? String(r.ItmsGrpNam) : ""}</td>
                  <td>{r.Canceled != null ? String(r.Canceled) : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="sap-modal-foot">
          <button type="button" className="sap-btn primary" onClick={() => confirmPick()} disabled={sel == null}>
            OK
          </button>
          <button type="button" className="sap-btn" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
