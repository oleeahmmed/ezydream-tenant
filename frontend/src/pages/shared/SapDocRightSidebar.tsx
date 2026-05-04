import { resolveSelectControlState, type FieldChoiceLookup } from "../../lib/useFieldChoiceLookup";
import { SapDateField } from "../../ui/SapDateField";
import type { HeaderField } from "./documentTypes";
import type { Row } from "./formset";

type SapDocRightSidebarProps = {
  keys: string[];
  headerFields: HeaderField[];
  form: Row;
  setField: (key: string, v: string) => void;
  canUpdate: boolean;
  /** When set, known coded fields render as labeled dropdowns instead of raw text. */
  choiceLookup?: FieldChoiceLookup | null;
  /** Title bar “close” (hides the column via workspace). */
  onRequestClose?: () => void;
};

/** SAP B1–style right column — matches ``frontend/ui/index.html`` UDF panel (title bar + 115px / 1fr grid). */
export function SapDocRightSidebar({
  keys,
  headerFields,
  form,
  setField,
  canUpdate,
  choiceLookup,
  onRequestClose,
}: SapDocRightSidebarProps) {
  const ks = keys.filter((k) => headerFields.some((h) => h.key === k));
  if (ks.length === 0) return null;

  function renderOne(h: HeaderField) {
    const v = form[h.key] != null ? String(form[h.key]) : "";
    const ro = !canUpdate || h.readonly;
    const gid = choiceLookup?.hints[h.key];
    const opts = gid ? choiceLookup.groupMap.get(gid) : undefined;
    const useTextarea =
      h.key === "Comments" ||
      h.key === "JrnlMemo" ||
      h.label.toLowerCase().includes("remark") ||
      h.label.toLowerCase().includes("memo") ||
      h.label.toLowerCase().includes("comments");

    if (h.kind === "date") {
      return <SapDateField readOnly={ro} value={v} onChange={(next) => setField(h.key, next)} aria-label={h.label} />;
    }
    if (useTextarea) {
      return (
        <textarea
          className={"rp-textarea" + (ro ? " readonly" : "")}
          readOnly={ro}
          rows={8}
          value={v}
          onChange={ro ? undefined : (e) => setField(h.key, e.target.value)}
          aria-label={h.label}
        />
      );
    }
    if (opts?.length) {
      const { selectValue, needsUnknownOption } = resolveSelectControlState(v, opts);
      return (
        <select
          className={"rp-field-select" + (ro ? " readonly" : "")}
          aria-label={h.label}
          disabled={ro}
          value={selectValue}
          onChange={
            ro
              ? undefined
              : (e) => {
                  const raw = e.target.value;
                  if (h.kind === "number") {
                    setField(h.key, raw === "" ? "" : String(Number(raw)));
                  } else {
                    setField(h.key, raw);
                  }
                }
          }
        >
          <option value="">—</option>
          {needsUnknownOption ? <option value={selectValue}>{selectValue}</option> : null}
          {opts.map((o) => (
            <option key={`${gid}:${String(o.value)}`} value={String(o.value)}>
              {o.label}
            </option>
          ))}
        </select>
      );
    }
    return (
      <input
        className={"rp-input" + (ro ? " readonly" : "")}
        readOnly={ro}
        type={h.kind === "number" ? "number" : "text"}
        value={v}
        onChange={ro ? undefined : (e) => setField(h.key, e.target.value)}
        aria-label={h.label}
      />
    );
  }

  return (
    <aside className="right-panel" aria-label="User-defined fields">
      <div className="rp-titlebar">
        <div className="rp-nav-btn" aria-hidden>
          ◀
        </div>
        <div className="rp-nav-btn" style={{ marginRight: 4 }} aria-hidden>
          ▶
        </div>
        <select className="rp-select" aria-label="User-defined field category" defaultValue="udfs">
          <option value="udfs">User-Defined Fields</option>
        </select>
        {onRequestClose ? (
          <span className="rp-close" title="Hide panel" onClick={onRequestClose} onKeyDown={(e) => e.key === "Enter" && onRequestClose()} role="button" tabIndex={0}>
            ×
          </span>
        ) : null}
      </div>
      <div className="rp-body">
        {ks.map((key) => {
          const hf = headerFields.find((h) => h.key === key);
          if (!hf) return null;
          return (
            <div key={key} className={"rp-row" + (isTextareaField(hf) ? " rp-row--top" : "")}>
              <span className="rp-label" title={hf.label}>
                {hf.label}
              </span>
              <div className="rp-control">{renderOne(hf)}</div>
            </div>
          );
        })}
      </div>
    </aside>
  );
}

function isTextareaField(h: HeaderField): boolean {
  return (
    h.key === "Comments" ||
    h.key === "JrnlMemo" ||
    h.label.toLowerCase().includes("remark") ||
    h.label.toLowerCase().includes("memo") ||
    h.label.toLowerCase().includes("comments")
  );
}
