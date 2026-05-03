import type { SalesRegistryEntry } from "../registry";

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
};

export function toInputDate(v: unknown): string {
  if (v == null || v === "") return "";
  const s = String(v);
  if (s.length >= 10) return s.slice(0, 10);
  return s;
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
  };
}

export function formsetPad(rows: FormsetRow[]): FormsetRow[] {
  const x = [...rows];
  while (x.length < FORMSET_ROWS) x.push(emptyFormsetRow());
  return x.slice(0, FORMSET_ROWS);
}

export function apiLineToFormset(r: Row): FormsetRow {
  const base = emptyFormsetRow();
  return {
    ...base,
    ItemCode: String(r.ItemCode ?? ""),
    Dscription: String(r.Dscription ?? ""),
    Quantity: String(r.Quantity ?? "1"),
    Price: String(r.Price ?? "0"),
    DiscPrcnt: String(r.DiscPrcnt ?? "0"),
    WhsCode: String(r.WhsCode ?? "01"),
    LineTotal: String(r.LineTotal ?? "0"),
    __lineNum: r.LineNum != null ? Number(r.LineNum) : null,
  };
}

/** Blank formset slot until Item (or description) is set. */
export function formsetRowIsEmpty(r: FormsetRow): boolean {
  return r.ItemCode.trim() === "" && r.Dscription.trim() === "";
}

function cloneFormsetRow(r: FormsetRow): FormsetRow {
  return { ...r };
}

/** Recompute ``LineTotal`` for every row (after bulk row moves). */
export function formsetRefreshLineTotals(rows: FormsetRow[]): FormsetRow[] {
  return rows.map((r) => ({
    ...r,
    LineTotal: computeLineTotalString(r.Quantity, r.Price, r.DiscPrcnt),
  }));
}

/** Insert an empty row at ``i``, shifting rows at ``i..FORMSET_ROWS-2`` down; drops previous last row. */
export function formsetInsertEmptyAbove(rows: FormsetRow[], i: number): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  /** No free slot below to shift into when ``i`` is the last index. */
  if (i < 0 || i >= FORMSET_ROWS - 1) return formsetRefreshLineTotals(out);
  for (let j = FORMSET_ROWS - 1; j > i; j--) out[j] = cloneFormsetRow(out[j - 1]);
  out[i] = emptyFormsetRow();
  return formsetRefreshLineTotals(out);
}

/** Insert an empty row at ``i + 1``, shifting rows below; no-op if ``i >= FORMSET_ROWS - 1``. */
export function formsetInsertEmptyBelow(rows: FormsetRow[], i: number): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS - 1) return formsetRefreshLineTotals(out);
  for (let j = FORMSET_ROWS - 1; j > i + 1; j--) out[j] = cloneFormsetRow(out[j - 1]);
  out[i + 1] = emptyFormsetRow();
  return formsetRefreshLineTotals(out);
}

/** Remove row ``i`` by shifting rows ``i+1..`` up; last row becomes empty. */
export function formsetDeleteShiftUp(rows: FormsetRow[], i: number): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS) return formsetRefreshLineTotals(out);
  for (let j = i; j < FORMSET_ROWS - 1; j++) out[j] = cloneFormsetRow(out[j + 1]);
  out[FORMSET_ROWS - 1] = emptyFormsetRow();
  return formsetRefreshLineTotals(out);
}

/** Copy row ``i`` into ``i+1`` (new line has ``__lineNum: null``); shifts lower rows down. */
export function formsetDuplicateBelow(rows: FormsetRow[], i: number): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS - 1) return formsetRefreshLineTotals(out);
  for (let j = FORMSET_ROWS - 1; j > i + 1; j--) out[j] = cloneFormsetRow(out[j - 1]);
  const dup = cloneFormsetRow(out[i]);
  dup.__lineNum = null;
  out[i + 1] = dup;
  return formsetRefreshLineTotals(out);
}

/** Clear item fields; keep ``__lineNum`` so save still deletes server line when empty. */
export function formsetClearRowInPlace(rows: FormsetRow[], i: number): FormsetRow[] {
  const out = formsetPad(rows).map(cloneFormsetRow);
  if (i < 0 || i >= FORMSET_ROWS) return formsetRefreshLineTotals(out);
  const ln = out[i].__lineNum;
  const cleared: FormsetRow = { ...emptyFormsetRow(), __lineNum: ln };
  cleared.LineTotal = computeLineTotalString(cleared.Quantity, cleared.Price, cleared.DiscPrcnt);
  out[i] = cleared;
  return formsetRefreshLineTotals(out);
}

export function formsetRowToTsv(r: FormsetRow): string {
  return [r.ItemCode, r.Dscription, r.Quantity, r.Price, r.DiscPrcnt, r.WhsCode].join("\t");
}

export function formsetNonEmptyRowsToTsv(rows: FormsetRow[]): string {
  return formsetPad(rows)
    .filter((r) => !formsetRowIsEmpty(r))
    .map(formsetRowToTsv)
    .join("\n");
}

/** First TSV line → row (pasted lines are treated as new, ``__lineNum: null``). */
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

export function buildCreateBody(def: SalesRegistryEntry, form: Row): Row {
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

export function buildPatchBody(def: SalesRegistryEntry, form: Row, orig: Row | null): Row {
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

export function buildLinePostJson(def: SalesRegistryEntry, docEntry: number, lineNum: number, r: FormsetRow): Row {
  const lineTotal = computeLineTotalString(r.Quantity, r.Price, r.DiscPrcnt);
  const o: Row = {
    DocEntry: docEntry,
    LineNum: lineNum,
    ItemCode: r.ItemCode.trim(),
    Dscription: r.Dscription || "",
    Quantity: r.Quantity || "1",
    Price: r.Price || "0",
    DiscPrcnt: r.DiscPrcnt || "0",
    WhsCode: r.WhsCode || "01",
    LineTotal: lineTotal,
  };
  if (def.lines.editKeys.includes("BaseType")) o.BaseType = null;
  if (def.lines.editKeys.includes("BaseEntry")) {
    o.BaseEntry = null;
    o.BaseLine = null;
  }
  return o;
}

export const LINE_PATCH_KEYS = new Set(["ItemCode", "Dscription", "Quantity", "Price", "DiscPrcnt", "WhsCode", "LineTotal"]);

/** Shown in ``sap-footer`` / totals (``frontend/ui/sap2.html``), not the two-column header. */
export const HEADER_FIELDS_IN_FOOTER = new Set(["Comments", "SlpCode", "OwnerCode", "DocTotal", "VatSum", "DiscSum"]);
