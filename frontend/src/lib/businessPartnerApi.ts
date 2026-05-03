import { apiFetch } from "./apiFetch";

type Row = Record<string, unknown>;

/** GET ``/api/business-partners/{card_code}`` — fills header CardName / Currency etc. */
export async function fetchBusinessPartner(cardCode: string): Promise<Row> {
  const code = cardCode.trim();
  if (!code) throw new Error("Empty CardCode");
  return apiFetch<Row>(`/api/business-partners/${encodeURIComponent(code)}`);
}
