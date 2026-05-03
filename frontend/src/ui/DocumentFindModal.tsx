import { useEffect, useState } from "react";

export type FindListCol = { key: string; label: string };

type DocumentFindModalProps = {
  open: boolean;
  title: string;
  filterLabel: string;
  filterValue: string;
  onFilterChange: (v: string) => void;
  columns: FindListCol[];
  rows: Record<string, unknown>[];
  busy: boolean;
  err: string;
  emptyHint?: string;
  onClose: () => void;
  onPick: (row: Record<string, unknown>, index: number) => void;
  onRefresh: () => void;
};

/** Choose-from-list modal: filter + grid; row click fills the caller form. */
export function DocumentFindModal({
  open,
  title,
  filterLabel,
  filterValue,
  onFilterChange,
  columns,
  rows,
  busy,
  err,
  emptyHint,
  onClose,
  onPick,
  onRefresh,
}: DocumentFindModalProps) {
  const [activeRow, setActiveRow] = useState<number | null>(null);

  useEffect(() => {
    if (open) setActiveRow(null);
  }, [open]);

  if (!open) return null;

  return (
    <div className="sap-modal-overlay" role="presentation" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="sap-modal-box sap-find-modal" role="dialog" aria-modal="true" aria-labelledby="sap-find-modal-title" onMouseDown={(e) => e.stopPropagation()}>
        <div className="sap-modal-head">
          <span id="sap-find-modal-title">{title}</span>
          <button type="button" className="sap-modal-close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>
        <div className="sap-modal-body">
          <div className="field-row" style={{ marginBottom: 8 }}>
            <span className="field-label">{filterLabel}</span>
            <input
              className="field-input field-input-grow"
              type="text"
              value={filterValue}
              onChange={(e) => onFilterChange(e.target.value)}
              placeholder="Type to narrow (e.g. 8)…"
              autoFocus
              aria-label={filterLabel}
            />
          </div>
          {err ? (
            <div className="sap-msg err" style={{ marginBottom: 6 }}>
              {err}
            </div>
          ) : null}
          <div className="grid-wrap sap-find-modal-grid">
            <table className="sap-table">
              <thead>
                <tr>
                  {columns.map((c) => (
                    <th key={c.key}>{c.label}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr
                    key={i}
                    className={activeRow === i ? "selected" : ""}
                    style={{ cursor: "pointer" }}
                    onClick={() => {
                      setActiveRow(i);
                      onPick(row, i);
                    }}
                  >
                    {columns.map((c) => (
                      <td key={c.key}>{row[c.key] != null ? String(row[c.key]) : ""}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {!busy && rows.length === 0 ? <p className="sap-msg" style={{ marginTop: 6 }}>{emptyHint ?? "No rows — adjust the filter or press Refresh."}</p> : null}
        </div>
        <div className="sap-modal-foot">
          <button type="button" className="sap-btn" onClick={onClose}>
            Cancel
          </button>
          <button type="button" className="sap-btn" onClick={() => onRefresh()} disabled={busy}>
            Refresh
          </button>
        </div>
        {busy ? <div className="sap-modal-busy">Loading…</div> : null}
      </div>
    </div>
  );
}
