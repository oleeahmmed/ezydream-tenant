import { useEffect, useRef } from "react";
import { FORMSET_ROWS } from "../pages/shared/formset";

export type LineGridCtxAction =
  | "cut"
  | "copy"
  | "copyTable"
  | "paste"
  | "delete"
  | "addRow"
  | "addAbove"
  | "addBelow"
  | "deleteRow"
  | "removeAbove"
  | "removeBelow"
  | "duplicateRow";

export type LineGridContextMenuProps = {
  open: boolean;
  x: number;
  y: number;
  /** Selected row index (0-based). */
  lineRowIndex: number;
  canMutate: boolean;
  onClose: () => void;
  onAction: (action: LineGridCtxAction) => void;
};

function CtxItem({
  icon,
  label,
  disabled,
  onPick,
}: {
  icon: string;
  label: string;
  disabled?: boolean;
  onPick: () => void;
}) {
  return (
    <div
      className={"ctx-item" + (disabled ? " ctx-item--disabled" : "")}
      role="menuitem"
      tabIndex={disabled ? -1 : 0}
      onClick={() => {
        if (disabled) return;
        onPick();
      }}
      onKeyDown={(e) => {
        if (disabled) return;
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onPick();
        }
      }}
    >
      <span className="ctx-icon" aria-hidden>
        {icon}
      </span>
      <span>{label}</span>
    </div>
  );
}

/** Right-click menu for the sales document line grid (``frontend/ui/index.html``-style). */
export function LineGridContextMenu({ open, x, y, lineRowIndex, canMutate, onClose, onAction }: LineGridContextMenuProps) {
  const rootRef = useRef<HTMLDivElement>(null);
  const i = lineRowIndex;
  const noAddAbove = i >= FORMSET_ROWS - 1;
  const noAddBelow = i >= FORMSET_ROWS - 1;
  const noDup = i >= FORMSET_ROWS - 1;
  const noRemoveAbove = i <= 0;
  const noRemoveBelow = i >= FORMSET_ROWS - 1;

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    const onDown = (e: MouseEvent) => {
      if (rootRef.current?.contains(e.target as Node)) return;
      onClose();
    };
    document.addEventListener("keydown", onKey);
    document.addEventListener("mousedown", onDown);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("mousedown", onDown);
    };
  }, [open, onClose]);

  if (!open) return null;

  const left = Math.min(x, typeof window !== "undefined" ? window.innerWidth - 230 : x);
  const top = Math.min(y, typeof window !== "undefined" ? window.innerHeight - 420 : y);

  return (
    <div
      ref={rootRef}
      className="ctx-menu ctx-menu--line-grid visible"
      style={{ left, top }}
      role="menu"
      onMouseDown={(e) => e.stopPropagation()}
    >
      <CtxItem icon="✂" label="Cut" disabled={!canMutate} onPick={() => onAction("cut")} />
      <CtxItem icon="📋" label="Copy" onPick={() => onAction("copy")} />
      <CtxItem icon="📌" label="Copy table" onPick={() => onAction("copyTable")} />
      <CtxItem icon="📄" label="Paste" disabled={!canMutate} onPick={() => onAction("paste")} />
      <div className="ctx-separator" />
      <CtxItem icon="✖" label="Delete" disabled={!canMutate} onPick={() => onAction("delete")} />
      <div className="ctx-separator" />
      <CtxItem icon="✚" label="Add row" disabled={!canMutate || noAddBelow} onPick={() => onAction("addRow")} />
      <CtxItem icon="↑" label="Add row above" disabled={!canMutate || noAddAbove} onPick={() => onAction("addAbove")} />
      <CtxItem icon="↓" label="Add row below" disabled={!canMutate || noAddBelow} onPick={() => onAction("addBelow")} />
      <CtxItem icon="✖" label="Delete row" disabled={!canMutate} onPick={() => onAction("deleteRow")} />
      <CtxItem icon="⌫" label="Remove row above" disabled={!canMutate || noRemoveAbove} onPick={() => onAction("removeAbove")} />
      <CtxItem icon="⌫" label="Remove row below" disabled={!canMutate || noRemoveBelow} onPick={() => onAction("removeBelow")} />
      <CtxItem icon="🔄" label="Duplicate row" disabled={!canMutate || noDup} onPick={() => onAction("duplicateRow")} />
    </div>
  );
}
