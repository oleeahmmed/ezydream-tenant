import type { DocumentRegistryEntry } from "./documentTypes";

export type Row = Record<string, unknown>;

/** Matches ``frontend/ui/sap2.html`` Contents grid row count. */
export const FORMSET_ROWS = 10;

export type FormsetRow = {
  ItemCode: string;
  Dscription: string;
  Quantity: string;
  Price: string;
  DiscPrcnt: string;
  WhsCode: string;
  LineTotal: string;
  /** Server LineNum when loaded from API; null = new / blank slot */
  __lineNum: number | null;
  LineStatus?: string;
  PlannedQty?: string;
  IssuedQty?: string;
  BaseType?: string;
  BaseEntry?: string;
  BaseLine?: string;
  /** Inventory / transfer lines */
  OpenQty?: string;
  FromWhsCod?: string;
  Account?: string;
  InQty?: string;
  OutQty?: string;
  Difference?: string;
  TargetType?: string;
  TrgetEntry?: string;
  BaseRef?: string;
};

export function toInputDate(v: unknown): string {
  if (v == null || v === "") return "";
  const s = String(v);
  const d = s.length >= 10 ? s.slice(0, 10) : s.trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(d)) return "";
  const ms = Date.parse(`${d}T12:00:00`);
  if (Number.isNaN(ms)) return "";
  return d;
}

export function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

export function emptyFormsetRow(): FormsetRow {
  return {
    ItemCode: "",
    Dscription: "",
    Quantity: "1",
    Price: "0",
    DiscPrcnt: "0",
    WhsCode: "01",
    LineTotal: "0",
    __lineNum: null,
    LineStatus: "O",
    PlannedQty: "0",
    IssuedQty: "0",
    BaseType: "",
    BaseEntry: "",
    BaseLine: "",
    OpenQty: "1",
    FromWhsCod: "01",
    Account: "",
    InQty: "0",
    OutQty: "0",
    Difference: "0",
    TargetType: "-1",
    TrgetEntry: "",
    BaseRef: "",
  };
}

export function formsetPad(rows: FormsetRow[]): FormsetRow[] {
  const x = [...rows];
  while (x.length < FORMSET_ROWS) x.push(emptyFormsetRow());
  return x.slice(0, FORMSET_ROWS);
}

export function apiLineToFormset(r: Row, editKeys?: string[]): FormsetRow {
  const base = emptyFormsetRow();
  const out: FormsetRow = {
    ...base,
    ItemCode: String(r.ItemCode ?? ""),
    Dscription: String(r.Dscription ?? ""),
    Quantity: String(r.Quantity ?? "1"),
    Price: String(r.Price ?? "0"),
    DiscPrcnt: String(r.DiscPrcnt ?? "0"),
    WhsCode: String(r.WhsCode ?? "01"),
    LineTotal: String(r.LineTotal ?? "0"),
    __lineNum: r.LineNum != null ? Number(r.LineNum) : null,
    LineStatus: r.LineStatus != null ? String(r.LineStatus) : base.LineStatus,
    PlannedQty: String(r.PlannedQty ?? r.Quantity ?? "0"),
    IssuedQty: String(r.IssuedQty ?? "0"),
    BaseType: r.BaseType != null ? String(r.BaseType) : "",
    BaseEntry: r.BaseEntry != null ? String(r.BaseEntry) : "",
    BaseLine: r.BaseLine != null ? String(r.BaseLine) : "",
    OpenQty: String(r.OpenQty ?? r.Quantity ?? "1"),
    FromWhsCod: String(r.FromWhsCod ?? ""),
    Account: String(r.Account ?? ""),
    InQty: String(r.InQty ?? "0"),
    OutQty: String(r.OutQty ?? "0"),
    Difference: String(r.Difference ?? "0"),
    TargetType: r.TargetType != null ? String(r.TargetType) : "-1",
    TrgetEntry: r.TrgetEntry != null ? String(r.TrgetEntry) : "",
    BaseRef: String(r.BaseRef ?? ""),
  };
  if (editKeys && !editKeys.includes("Dscription")) out.Dscription = "";
  if (editKeys && !editKeys.includes("DiscPrcnt")) out.DiscPrcnt = "0";
  if (editKeys && !editKeys.includes("LineTotal")) {
    out.LineTotal = editKeys.includes("DiscPrcnt")
      ? computeLineTotalString(out.Quantity, out.Price, out.DiscPrcnt)
      : lineNetNoDisc(out.Quantity, out.Price);
  }
  if (editKeys) {
    const o = out as unknown as Record<string, string>;
    for (const k of editKeys) {
      if (k === "LineNum" || k === "DocEntry") continue;
      if (r[k] === undefined || r[k] === null) continue;
      o[k] = String(r[k]);
    }
  }
  return out;
}

export function lineNetNoDisc(quantity: string, price: string): string {
  const qty = Number(String(quantity ?? "").replace(",", ".")) || 0;
  const pr = Number(String(price ?? "").replace(",", ".")) || 0;
  const net = qty * pr;
  if (!Number.isFinite(net)) return "0";
  return net.toFixed(2);
}

/** Blank line slot: item + optional description empty. */
export function formsetRowIsEmpty(r: FormsetRow, lineEditKeys?: string[]): boolean {
  const noItem = r.ItemCode.trim() === "";
  const useDesc = lineEditKeys == null || lineEditKeys.includes("Dscription");
  if (!useDesc) return noItem;
  return noItem && r.Dscription.trim() === "";
}

export function computeLineTotalString(quantity: string, price: string, discPrcnt: string): string {
  const qty = Number(String(quantity ?? "").replace(",", ".")) || 0;
  const pr = Number(String(price ?? "").replace(",", ".")) || 0;
  const disc = Number(String(discPrcnt ?? "").replace(",", ".")) || 0;
  const d = Math.min(100, Math.max(0, disc));
  const gross = qty * pr;
  const net = gross * (1 - d / 100);
  if (!Number.isFinite(net)) return "0";
  return net.toFixed(2);
}

function cloneFormsetRow(r: FormsetRow): FormsetRow {
  return { ...r };
}

export function formsetRefreshLineTotals(rows: FormsetRow[], editKeys: string[]): FormsetRow[] {
  return rows.map((r) => {
    if (!editKeys.includes("LineTotal")) return { ...r };
    const lt = editKeys.includes("DiscPrcnt")
      ? computeLineTotalString(r.Quantity, r.Price, r.DiscPrcnt)
      : lineNetNoDisc(r.Quantity, r.Price);
    return { ...r, LineTotal: lt };
  });
}

export function formsetInsertEmptyAbove(rows: FormsetRow[], i: number, editKeys: string[]): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS - 1) return formsetRefreshLineTotals(out, editKeys);
  for (let j = FORMSET_ROWS - 1; j > i; j--) out[j] = cloneFormsetRow(out[j - 1]);
  out[i] = emptyFormsetRow();
  return formsetRefreshLineTotals(out, editKeys);
}

export function formsetInsertEmptyBelow(rows: FormsetRow[], i: number, editKeys: string[]): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS - 1) return formsetRefreshLineTotals(out, editKeys);
  for (let j = FORMSET_ROWS - 1; j > i + 1; j--) out[j] = cloneFormsetRow(out[j - 1]);
  out[i + 1] = emptyFormsetRow();
  return formsetRefreshLineTotals(out, editKeys);
}

export function formsetDeleteShiftUp(rows: FormsetRow[], i: number, editKeys: string[]): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS) return formsetRefreshLineTotals(out, editKeys);
  for (let j = i; j < FORMSET_ROWS - 1; j++) out[j] = cloneFormsetRow(out[j + 1]);
  out[FORMSET_ROWS - 1] = emptyFormsetRow();
  return formsetRefreshLineTotals(out, editKeys);
}

export function formsetDuplicateBelow(rows: FormsetRow[], i: number, editKeys: string[]): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS - 1) return formsetRefreshLineTotals(out, editKeys);
  for (let j = FORMSET_ROWS - 1; j > i + 1; j--) out[j] = cloneFormsetRow(out[j - 1]);
  const dup = cloneFormsetRow(out[i]);
  dup.__lineNum = null;
  out[i + 1] = dup;
  return formsetRefreshLineTotals(out, editKeys);
}

export function formsetClearRowInPlace(rows: FormsetRow[], i: number, editKeys: string[]): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS) return formsetRefreshLineTotals(out, editKeys);
  const ln = out[i].__lineNum;
  const cleared: FormsetRow = { ...emptyFormsetRow(), __lineNum: ln };
  cleared.LineTotal = editKeys.includes("DiscPrcnt")
    ? computeLineTotalString(cleared.Quantity, cleared.Price, cleared.DiscPrcnt)
    : lineNetNoDisc(cleared.Quantity, cleared.Price);
  out[i] = cleared;
  return formsetRefreshLineTotals(out, editKeys);
}

export function formsetRowToTsv(r: FormsetRow): string {
  return [r.ItemCode, r.Dscription, r.Quantity, r.Price, r.DiscPrcnt, r.WhsCode].join("\t");
}

export function formsetNonEmptyRowsToTsv(rows: FormsetRow[], editKeys: string[]): string {
  return formsetPad(rows)
    .filter((r) => !formsetRowIsEmpty(r, editKeys))
    .map(formsetRowToTsv)
    .join("\n");
}

export function parseTsvLineToFormsetRow(line: string): FormsetRow | null {
  const raw = line.replace(/\r/g, "").trim();
  if (!raw) return null;
  const parts = raw.split("\t");
  const base = emptyFormsetRow();
  if (parts[0] != null && parts[0] !== "") base.ItemCode = parts[0];
  if (parts[1] != null) base.Dscription = parts[1];
  if (parts[2] != null && parts[2] !== "") base.Quantity = parts[2];
  if (parts[3] != null && parts[3] !== "") base.Price = parts[3];
  if (parts[4] != null && parts[4] !== "") base.DiscPrcnt = parts[4];
  if (parts[5] != null && parts[5] !== "") base.WhsCode = parts[5];
  base.__lineNum = null;
  base.LineTotal = computeLineTotalString(base.Quantity, base.Price, base.DiscPrcnt);
  if (formsetRowIsEmpty(base)) return null;
  return base;
}

export function buildCreateBody(def: DocumentRegistryEntry, form: Row): Row {
  const o: Row = {};
  for (const k of def.createKeys) {
    if (form[k] === undefined || form[k] === "") continue;
    const f = def.headerFields.find((h) => h.key === k);
    if (f?.kind === "number") {
      const n = Number(form[k]);
      if (!Number.isFinite(n)) continue;
      o[k] = n;
    } else o[k] = form[k];
  }
  return o;
}

export function buildPatchBody(def: DocumentRegistryEntry, form: Row, orig: Row | null): Row {
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

function numOrNull(s: string | undefined): number | null {
  const t = String(s ?? "").trim();
  if (t === "") return null;
  const n = Number(t.replace(",", "."));
  return Number.isFinite(n) ? n : null;
}

/** Build POST JSON for a document line from ``editKeys`` and formset row. */
export function buildLinePostJson(def: DocumentRegistryEntry, parentPk: string | number, lineNum: number, r: FormsetRow): Row {
  const editKeys = def.lines.editKeys;
  const bind = def.lines.lineParentFieldInBody ?? "DocEntry";
  const o: Row = { LineNum: lineNum };
  if (bind === "Father") o.Father = String(parentPk);
  else o.DocEntry = Number(parentPk);

  for (const k of editKeys) {
    if (k === "DocEntry" || k === "Father" || k === "LineNum") continue;
    if (k === "Canceled") continue;
    if (k === "ItemCode") {
      o.ItemCode = r.ItemCode.trim();
      continue;
    }
    if (k === "Dscription") {
      o.Dscription = r.Dscription || "";
      continue;
    }
    if (k === "Quantity") {
      o.Quantity = r.Quantity || "1";
      continue;
    }
    if (k === "Price") {
      o.Price = r.Price || "0";
      continue;
    }
    if (k === "DiscPrcnt") {
      o.DiscPrcnt = r.DiscPrcnt || "0";
      continue;
    }
    if (k === "WhsCode") {
      o.WhsCode = r.WhsCode || "01";
      continue;
    }
    if (k === "LineTotal") {
      o.LineTotal = editKeys.includes("DiscPrcnt")
        ? computeLineTotalString(r.Quantity, r.Price, r.DiscPrcnt)
        : lineNetNoDisc(r.Quantity, r.Price);
      continue;
    }
    if (k === "LineStatus") {
      o.LineStatus = (String(r.LineStatus || "O")).trim().toUpperCase().slice(0, 1) || "O";
      continue;
    }
    if (k === "PlannedQty") {
      o.PlannedQty = r.PlannedQty || "0";
      continue;
    }
    if (k === "IssuedQty") {
      o.IssuedQty = r.IssuedQty || "0";
      continue;
    }
    if (k === "BaseType") {
      o.BaseType = numOrNull(r.BaseType);
      continue;
    }
    if (k === "BaseEntry") {
      o.BaseEntry = numOrNull(r.BaseEntry);
      continue;
    }
    if (k === "BaseLine") {
      o.BaseLine = numOrNull(r.BaseLine);
      continue;
    }
    if (k === "OpenQty") {
      o.OpenQty = (r as FormsetRow).OpenQty != null && (r as FormsetRow).OpenQty !== "" ? String((r as FormsetRow).OpenQty) : r.Quantity || "1";
      continue;
    }
    if (k === "FromWhsCod") {
      o.FromWhsCod = String((r as FormsetRow).FromWhsCod ?? "");
      continue;
    }
    if (k === "Account") {
      o.Account = String((r as FormsetRow).Account ?? "");
      continue;
    }
    if (k === "InQty") {
      o.InQty = String((r as FormsetRow).InQty ?? "0");
      continue;
    }
    if (k === "OutQty") {
      o.OutQty = String((r as FormsetRow).OutQty ?? "0");
      continue;
    }
    if (k === "Difference") {
      o.Difference = String((r as FormsetRow).Difference ?? "0");
      continue;
    }
    if (k === "TargetType") {
      const t = String((r as FormsetRow).TargetType ?? "").trim();
      o.TargetType = t === "" ? -1 : Number(t.replace(",", ".")) || -1;
      continue;
    }
    if (k === "TrgetEntry") {
      o.TrgetEntry = numOrNull(String((r as FormsetRow).TrgetEntry ?? ""));
      continue;
    }
    if (k === "BaseRef") {
      o.BaseRef = String((r as FormsetRow).BaseRef ?? "");
      continue;
    }
  }
  return o;
}

export function linePatchKeySet(def: DocumentRegistryEntry): Set<string> {
  return new Set(def.lines.editKeys.filter((k) => k !== "LineNum"));
}

/** Shown in ``sap-footer`` / totals (``frontend/ui/sap2.html``), not the two-column header. */
export const DEFAULT_HEADER_FIELDS_IN_FOOTER = new Set(["Comments", "SlpCode", "OwnerCode", "DocTotal", "VatSum", "DiscSum"]);
export const HEADER_FIELDS_IN_FOOTER = DEFAULT_HEADER_FIELDS_IN_FOOTER;
