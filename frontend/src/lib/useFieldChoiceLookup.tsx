import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { apiFetch } from "./apiFetch";

export type ChoiceOption = { value: string | number; label: string };

export type FieldHintsByListPathPrefixRow = { prefix: string; hints: Record<string, string> };

export type FieldChoicesPayload = {
  groups: { id: string; options: ChoiceOption[] }[];
  fieldHints: Record<string, string>;
  fieldHintsByListPathPrefix?: FieldHintsByListPathPrefixRow[];
};

export type FieldChoiceLookup = {
  groupMap: Map<string, ChoiceOption[]>;
  hints: Record<string, string>;
};

/** Raw catalog from API, or loading / missing. ``undefined`` = no React provider (fallback fetch in hook). */
type FieldChoicesContextValue = FieldChoicesPayload | null | "loading" | undefined;

const FieldChoicesRawContext = createContext<FieldChoicesContextValue>(undefined);

/**
 * Fetch field-choice catalog once for the whole authenticated app (dashboard).
 * Without this provider, ``useFieldChoiceLookup`` falls back to fetching per screen (slower, duplicates).
 */
export function FieldChoicesProvider({ children }: { children: ReactNode }) {
  const [raw, setRaw] = useState<FieldChoicesPayload | null | "loading">("loading");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await apiFetch<FieldChoicesPayload>("/api/meta/field-choices");
        if (!cancelled) setRaw(r);
      } catch {
        if (!cancelled) setRaw(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return <FieldChoicesRawContext.Provider value={raw}>{children}</FieldChoicesRawContext.Provider>;
}

function normalizeListPath(p: string): string {
  const q = p.split("?")[0] ?? "";
  return q.replace(/\/+$/, "") || q;
}

/** Merge global field hints with the longest matching ``listPath`` prefix (same rules as backend). */
export function mergeFieldHintsWithListPath(raw: FieldChoicesPayload, listPath?: string | null): FieldChoiceLookup {
  const groupMap = new Map<string, ChoiceOption[]>();
  for (const g of raw.groups ?? []) {
    groupMap.set(g.id, g.options ?? []);
  }
  const merged: Record<string, string> = { ...(raw.fieldHints ?? {}) };
  const lp = normalizeListPath((listPath ?? "").trim());
  if (lp) {
    const rows = [...(raw.fieldHintsByListPathPrefix ?? [])].sort((a, b) => b.prefix.length - a.prefix.length);
    for (const row of rows) {
      const pre = normalizeListPath(row.prefix.trim());
      if (!pre) continue;
      if (lp === pre || lp.startsWith(`${pre}/`)) {
        Object.assign(merged, row.hints ?? {});
        break;
      }
    }
  }
  return { groupMap, hints: merged };
}

/**
 * Map persisted/API values to an ``<option value>`` string so the select stays controlled.
 * Handles trim/space, case for single-letter codes, and numeric option values from string forms.
 */
export function coalesceSelectStringValue(v: string, options: ChoiceOption[] | undefined): string {
  if (!options?.length) return v;
  const t = v.trim();
  if (t === "") return "";
  if (options.some((o) => String(o.value) === t)) return t;
  for (const o of options) {
    if (typeof o.value === "string" && String(o.value).trim().toUpperCase() === t.toUpperCase()) {
      return String(o.value);
    }
  }
  for (const o of options) {
    if (typeof o.value === "number") {
      const n = Number(t);
      if (!Number.isNaN(n) && n === o.value) return String(o.value);
    }
  }
  return "";
}

/**
 * HTML ``<select>`` must have a matching ``<option>`` for the current value. If the API returns a
 * code not in the static catalog (e.g. a currency), we still show it and add a synthetic option.
 */
export function resolveSelectControlState(
  v: string,
  options: ChoiceOption[] | undefined,
): { selectValue: string; needsUnknownOption: boolean } {
  if (!options?.length) return { selectValue: v.trim(), needsUnknownOption: false };
  const t = v.trim();
  if (t === "") return { selectValue: "", needsUnknownOption: false };
  const matched = coalesceSelectStringValue(t, options);
  if (matched !== "") return { selectValue: matched, needsUnknownOption: false };
  return { selectValue: t, needsUnknownOption: true };
}

/**
 * Resolve merged hints + option groups for the current screen.
 * Pass the document registry ``listPath`` (e.g. ``/api/finance/journal-entries``).
 */
export function useFieldChoiceLookup(listPath?: string | null): FieldChoiceLookup | null {
  const fromCtx = useContext(FieldChoicesRawContext);
  const [localRaw, setLocalRaw] = useState<FieldChoicesPayload | null>(null);
  const [localReady, setLocalReady] = useState(false);

  useEffect(() => {
    if (fromCtx !== undefined) return;
    let cancelled = false;
    (async () => {
      try {
        const r = await apiFetch<FieldChoicesPayload>("/api/meta/field-choices");
        if (!cancelled) setLocalRaw(r);
      } catch {
        if (!cancelled) setLocalRaw(null);
      } finally {
        if (!cancelled) setLocalReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [fromCtx]);

  return useMemo(() => {
    let payload: FieldChoicesPayload | null = null;
    if (fromCtx !== undefined) {
      if (fromCtx === "loading") return null;
      payload = fromCtx;
    } else {
      if (!localReady) return null;
      payload = localRaw;
    }
    if (!payload) return null;
    return mergeFieldHintsWithListPath(payload, listPath);
  }, [fromCtx, localRaw, localReady, listPath]);
}
