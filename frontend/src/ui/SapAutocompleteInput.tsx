import type { InputHTMLAttributes } from "react";

import { SearchTriggerIcon } from "./SearchTriggerIcon";

export type SapAutocompleteInputProps = Omit<InputHTMLAttributes<HTMLInputElement>, "className"> & {
  /** Classes on the outer wrapper (e.g. ``sap-input-autocomplete--cell``). */
  wrapperClassName?: string;
  /** Classes on the ``<input>`` (e.g. ``field-input field-input-grow`` or ``cell-input``). */
  inputClassName?: string;
  onOpenList: () => void;
  /** Tooltip / aria for the embedded list button. */
  listButtonTitle?: string;
  /** If true, no embedded button (same as read-only look). */
  hideTrigger?: boolean;
  /**
   * If true, the text box stays read-only but the choose-from-list button remains visible.
   * Use when the field shows a resolved label/name while the API stores a code (Item group, etc.).
   */
  keepTriggerWhenReadOnly?: boolean;
};

/**
 * Enterprise-style field: cream background, **list trigger inside** on the right (search icon).
 */
export function SapAutocompleteInput({
  wrapperClassName = "",
  inputClassName = "",
  onOpenList,
  listButtonTitle = "Choose from list",
  readOnly,
  disabled,
  hideTrigger,
  keepTriggerWhenReadOnly,
  ...inputProps
}: SapAutocompleteInputProps) {
  const noTrigger = Boolean(hideTrigger || disabled || (readOnly && !keepTriggerWhenReadOnly));
  return (
    <div
      className={`sap-input-autocomplete${noTrigger ? " sap-input-autocomplete--readonly" : ""}${wrapperClassName ? ` ${wrapperClassName}` : ""}`.trim()}
    >
      <input
        {...inputProps}
        readOnly={readOnly}
        disabled={disabled}
        className={`sap-input-autocomplete__field${inputClassName ? ` ${inputClassName}` : ""}`.trim()}
      />
      {!noTrigger ? (
        <button
          type="button"
          className="sap-input-autocomplete__trigger"
          title={listButtonTitle}
          aria-label={listButtonTitle}
          onMouseDown={(e) => {
            e.preventDefault();
            e.stopPropagation();
          }}
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onOpenList();
          }}
        >
          <SearchTriggerIcon />
        </button>
      ) : null}
    </div>
  );
}
