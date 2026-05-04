import { useRef, type InputHTMLAttributes } from "react";

type SapDateFieldProps = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "type" | "value" | "onChange" | "size"
> & {
  value: string;
  onChange: (isoDate: string) => void;
};

/** SAP B1–style date row: native date input plus calendar affordance (calendar picker where supported). */
export function SapDateField({ className = "", value, onChange, readOnly, disabled, ...rest }: SapDateFieldProps) {
  const ref = useRef<HTMLInputElement>(null);
  const ro = Boolean(readOnly || disabled);

  function openPicker() {
    const el = ref.current;
    if (!el || ro) return;
    try {
      el.showPicker?.();
    } catch {
      el.focus();
    }
  }

  return (
    <div className={"sap-date-field" + (ro ? " sap-date-field--readonly" : "")}>
      <input
        ref={ref}
        className={"sap-date-field__input " + className}
        type="date"
        value={value}
        readOnly={readOnly}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        {...rest}
      />
      <button
        type="button"
        className="sap-date-field__cal"
        tabIndex={-1}
        title="Calendar"
        disabled={ro}
        onClick={openPicker}
        aria-label="Open calendar"
      >
        <span className="sap-date-field__cal-icon" aria-hidden>
          ▦
        </span>
      </button>
    </div>
  );
}
