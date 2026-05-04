function toNoticeString(v: unknown): string {
  if (v == null) return "";
  if (typeof v === "string") return v;
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  if (v instanceof Error) return v.message;
  if (typeof v === "object") {
    if ("message" in v && typeof (v as { message: unknown }).message === "string") {
      return (v as { message: string }).message;
    }
    try {
      return JSON.stringify(v);
    } catch {
      return String(v);
    }
  }
  return String(v);
}

/** Exported for document status bar (inline message color). */
export function documentNoticeLevel(err: string, msg: string): "error" | "warning" | "success" | "info" {
  if (err.trim()) return "error";
  const m = msg.trim();
  if (!m) return "info";
  if (/warning/i.test(m)) return "warning";
  if (/(created|updated|loaded|saved|deleted|record loaded|line updated|line removed)/i.test(m)) return "success";
  return "info";
}

type DocumentNotificationStripProps = {
  err?: string | unknown;
  msg?: string | unknown;
};

/** Full-width bottom bar — error / warning / success / info (always at window foot). */
export function DocumentNotificationStrip({ err, msg }: DocumentNotificationStripProps) {
  const errS = toNoticeString(err).trim();
  const msgS = toNoticeString(msg).trim();
  const text = errS || msgS;
  if (!text) return null;
  const level = documentNoticeLevel(errS, msgS);
  return (
    <div className={`ez-doc-notification ez-doc-notification--${level}`} role="status" aria-live="polite">
      {level === "error" ? (
        <span className="ez-doc-notification__icon" aria-hidden>
          ✕
        </span>
      ) : level === "warning" ? (
        <span className="ez-doc-notification__icon" aria-hidden>
          ⚠
        </span>
      ) : level === "success" ? (
        <span className="ez-doc-notification__icon" aria-hidden>
          ✓
        </span>
      ) : (
        <span className="ez-doc-notification__icon" aria-hidden>
          ℹ
        </span>
      )}
      <span className="ez-doc-notification__text">{errS ? errS : msgS}</span>
    </div>
  );
}
