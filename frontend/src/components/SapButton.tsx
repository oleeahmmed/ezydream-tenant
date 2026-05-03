import type { ReactNode } from "react";

type SapButtonProps = {
  children: ReactNode;
  primary?: boolean;
  type?: "button" | "submit";
  disabled?: boolean;
  onClick?: () => void;
};

/** Enterprise-style button (``frontend/ui/sap-dash.html`` ``.btn-sap``). */
export function SapButton({ children, primary, type = "button", disabled, onClick }: SapButtonProps) {
  const cls = primary ? "btn-sap primary" : "btn-sap";
  return (
    <button type={type} className={cls} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
