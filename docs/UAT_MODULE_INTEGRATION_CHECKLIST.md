# UAT — মডিউল × API × পিছনের ইফেক্ট (SAP B1–স্টাইল ইন্টিগ্রেশন)

এই চেকলিস্ট দিয়ে তুমি **কোন API কলের পর ডাটাবেসে কী হওয়া উচিত** যাচাই করতে পারবে। পাস = প্রত্যাশিত টেবিলে পরিবর্তন; ফেইল = গ্যাপ বা কনফিগ বাকি।

**বেস URL (Bolt):** tenant অনুযায়ী; নিচে path শুধু suffix।  
**অথ:** Bearer JWT (`/api/auth/...`)।  
**ডুপ্লিকেট রুট:** অনেক মডিউলে **readable path** + **SAP alias** (যেমন `/oact`, `/ojdt`) একই ভিউতে যায়।

---

## ০) আগে থেকেই (প্রেরিকুজিট)

| # | কাজ | কেন |
|---|------|------|
| P1 | `OACT` এ কমপক্ষে **postable** ডিফল্ট GL অ্যাকাউন্ট তৈরি | `FINANCE_GL_*` সেটিংস (`posting_defaults.py`) এগুলো পয়েন্ট করবে |
| P2 | Django `settings` এ **`FINANCE_GL_AR`**, `FINANCE_GL_SALES_REVENUE`, `FINANCE_GL_AP`, `FINANCE_GL_PURCHASE_EXPENSE`, `FINANCE_GL_CASH` ইত্যাদি সেট | অটো জার্নাল ছাড়া বা `ValidationError` |
| P3 | `OWHS` এ কমপক্ষে একটা **Inactive=N** গুদাম | লাইনের `WhsCode` ভ্যালিডেশন |
| P4 | `OITM` এ আইটেম, **`InvntItem=Y`** যদি স্টক ট্র্যাক চাও | `OINM`/`OITW` আপডেট শুধু তখনই |
| P5 | `OCRD` বিজনেস পার্টনার + `CardCode` সেলস/ফাইন্যান্স ডকে মিল রাখো | রোলআপ / জার্নাল `ShortName` |

---

## ১) ফাইন্যান্স (`/api/finance`)

| API (উদাহরণ path) | অ্যাকশন | প্রত্যাশিত পিছনে |
|-------------------|---------|-------------------|
| `POST …/chart-of-accounts` | নতুন GL | `OACT` রো; `CurrTotal` জার্নাল থেকে অটো রোল আপ **নয়** (কোড অনুযায়ী) |
| `POST …/journal-entries` + লাইন | ম্যানুয়াল জার্নাল | `OJDT`/`JDT1` |
| `POST/PATCH/DELETE …/incoming-payments` বা `…/orct` | হেডার/লাইন | `sync_incoming_payment_journal` → **`OJDT`/`JDT1`** (`Ref1` = `AUTOJE:ORCT:…`); PATCH এ BP রোলআপ |
| `POST/PATCH/DELETE …/outgoing-payments` বা `…/ovpm` | হেডার/লাইন | `sync_outgoing_payment_journal` → **`OJDT`/`JDT1`** |
| `POST/PATCH …` ইনভয়েস (সেলস থেকে) | দেখ নিচে সেলস টেবিল | এখানে সরাসরি নয়; সেলস `OINV` থেকে `sync_ar_invoice_journal` |
| জার্নাল লাইন / বাজেট লাইন / পেমেন্ট লাইন | `GET/POST` …`/journal-entry-lines`, …`/budget-lines`, …`/incoming-payment-lines`, …`/outgoing-payment-lines` | ফ্রন্ট: Finance / Banking মেনু — `frontend/src/pages/finance/erpBoltRegistry.ts` |

**যাচাই (SQL / অ্যাডমিন):**

- `OJDT` এ `Ref1` LIKE `AUTOJE:%` কি তৈরি/আপডেট হয়।
- `JDT1` ডেবিট = ক্রেডিট (ব্যালান্সড)।
- `FINANCE_ENFORCE_OFPR` চালু থাকলে বন্ধ পিরিয়ডে **400** পাওয়া স্বাভাবিক।

---

## ২) সেলস A/R (`/api/sales`)

| API | অ্যাকশন | `OINM` / `OITW` | `OJDT`/`JDT1` | `OCRD` রোলআপ |
|-----|---------|-----------------|---------------|--------------|
| ডেলিভারি হেডার PATCH/DELETE | `resync_all_delivery_lines` | ✅ লাইন অনুযায়ী | — | — |
| ডেলিভারি লাইন POST/PATCH/DELETE | `sync_delivery_line_stock` | ✅ (ওপেন `DocStatus`, `Canceled=N`) | — | — |
| রিটার্ন হেডার/লাইন | `resync_*` / `sync_return_line_stock` | ✅ ইন স্টক | — | — |
| সেলস অর্ডার লাইন POST ইত্যাদি | `rebuild_oitw_*` + `recalculate_bp_rollups` | ❌ সাধারণত **অর্ডার স্টক মুভ করে না** (B1-এও ডেলিভারি পর্যায়ে মুভ) | — | ✅ `OrdersBal` প্রভাবিত হতে পারে |
| ইনভয়েস লাইন POST/PATCH/DELETE | `sync_ar_invoice_journal` | — | ✅ `AUTOJE:OINV:…` | ✅ `Balance` (ইনভয়েস টোটাল) |

**ফ্রন্ট রেফ:** `frontend/src/pages/sales/registry.ts` → `API = "/api/sales"`।

---

## ৩) পারচেজ A/P (`/api/purchase`)

| API | অ্যাকশন | `OINM` / `OITW` | `OJDT`/`JDT1` | `OCRD` / ইনভেন্টরি টোটাল |
|-----|---------|-----------------|---------------|---------------------------|
| GRPO হেডার/লাইন | `resync_all_grpo_lines` / `sync_grpo_line_stock` | ✅ ইন স্টক | — | `async_rebuild_inventory_totals_after_purchase_document_change` |
| ভেন্ডর রিটার্ন | `sync_vendor_return_line_stock` | ✅ | — | রিবিল্ড |
| A/P ইনভয়েস লাইন | `sync_ap_invoice_journal` | — | ✅ `AUTOJE:OPCH:…` | রিবিল্ড / BP কিছু পথে |
| পারচেজ অর্ডার লাইন | রিবিল্ড + BP | ❌ GRPO না হলে স্টক মুভ নয় | — | ✅ `OrdersBal` (OPOR) |

**ফ্রন্ট:** `frontend/src/pages/purchase/registry.ts`।

---

## ৪) ইনভেন্টরি (`/api/inventory`)

| API গ্রুপ | স্টক ইঞ্জিন | নোট |
|-----------|-------------|------|
| গুডস রিসিপ্ট / ইস্যু লাইন | `sync_goods_receipt_line_stock` / `sync_goods_issue_line_stock` | `OINM` + `OITW`/`OITM` (`InvntItem=Y`) |
| স্টক ট্রান্সফার লাইন | `sync_transfer_line_stock` | উভয় গুদাম |
| স্টক টেক / পোস্টিং | `post_oinm…` / `reverse_oinm…` (ভিউ অনুযায়ী) | `InventoryPostingDetailView` PATCH এ `Canceled` টগল |
| আইটেম মাস্টার | সাধারণত সরাসরি `OINM` নয় | `OnHand` সিঙ্ক স্টক পোস্টিং থেকে |

**লিস্ট কুয়েরি:** লাইন লিস্টে `doc_entry` / `trans_id` query (Bolt `request.query`) — ডক দেখে ডক।

**ফ্রন্ট:** `frontend/src/pages/inventory/registry.ts`, `InventoryDocumentCrud.tsx` (`INV_API`).

---

## ৫) বিজনেস পার্টনার (`/api/business-partners`)

| ট্রিগার | `OCRD` ফিল্ড |
|---------|---------------|
| `recalculate_bp_rollups(CardCode)` | `OrdersBal`, `DNotesBal`, `Balance` (সংক্ষিপ্ত ফর্মুলা — পূর্ণ B1 AR নয়) |

**কখন কল হয়:** উদাহরণ — ইনকামিং পেমেন্ট, কিছু সেলস লাইন পরিবর্তন।

**ফ্রন্ট:** `BUSINESS_PARTNER_API_ROOT` (`/api/business-partners`) — `frontend/src/pages/finance/business-partner/businessPartnerRegistry.ts` + Finance মেনু।

---

## ৬) ওয়্যারহাউজ (`/api/warehouse`)

| API | পিছনে |
|-----|--------|
| CRUD `OWHS` | মাস্টার; স্টক লজিক সরাসরি নয় |

**ফ্রন্ট:** `frontend/src/pages/warehouse/registry.ts` — সাইডবার **Warehouse → Warehouses (OWHS)** (`/warehouse/warehouses`).

---

## ৭) প্রোডাকশন (`/api/production`)

| API | পিছনে |
|-----|--------|
| BOM / প্রোডাকশন অর্ডার CRUD | মডেল টেবিল (`OITT`, `OWOR` ইত্যাদি) |
| স্টক ইস্যু/রিসিপ্ট | **ইনভেন্টরি মডিউলের ডকুমেন্ট API** দিয়ে (ডকস্ট্রিং অনুযায়ী `BaseType=202` ইত্যাদি) — এখানে অটো পোস্ট নয় |

---

## ৮) দ্রুত পাস/ফেইল চেক (টেস্ট সিকোয়েন্স)

1. **GL সেটআপ** → P2 কমপ্লিট।  
2. **আইটেম + গুদাম** → P3,P4।  
3. **GRPO লাইন** (পারচেজ) → `OINM` নতুন রো, `OITW.OnHand` বেড়েছে।  
4. **ডেলিভারি লাইন** (সেলস) → `OnHand` কমেছে (আউট)।  
5. **ইনভয়েস** → `OJDT` এ `AUTOJE:OINV:…`।  
6. **ইনকামিং পেমেন্ট** → `AUTOJE:ORCT:…` + `OCRD.Balance` পরিবর্তন।  

যে ধাপে কিছু না ঘটে — **সেটিংস**, **`DocStatus`/`Canceled`**, **`InvntItem`**, বা **এন্ডপয়েন্টে সিঙ্ক না বাঁধা** — তিনটার একটা।

---

## ৯) জানা সীমা (এই চেকলিস্ট “ফেইল” হিসেবে নয় — প্রোডাক্ট স্কোপ)

- `OACT.CurrTotal` = সব `JDT1` থেকে রোলআপ **ইমপ্লিমেন্টেড নয়**।  
- BP `Balance` = সরলীকৃত (পূর্ণ ওপেন আইটেম / মাল্টি-কারেন্সি নয়)।  
- কোটেশন / অর্ডার থেকে **স্বয়ংক্রিয় ডেলিভারি-ইনভয়েস চেইন** UI থেকে গ্যারান্টি নয় — API আলাদা।  
- SAP B1 **রিপোর্ট, অনুমোদন, ব্যাংক রিকন, সিরিয়াল/ব্যাচ** ইত্যাদি এখানে পূর্ণ নয়।

---

## ১০) ফাইল ম্যাপ (ডেভ রিফারেন্স)

| বিষয় | পাথ |
|------|------|
| স্টক পোস্টিং 코র | `apps/inventory/services/stock_posting.py` |
| ডকুমেন্ট → স্টক | `apps/inventory/services/document_stock.py` |
| ইনভেন্টরি টোটাল রিবিল্ড | `apps/inventory/services/inventory_totals.py` |
| অটো FI জার্নাল | `apps/finance/services/auto_journal.py` |
| GL সেটিংস | `apps/finance/services/posting_defaults.py` |
| BP রোলআপ | `apps/businesspartner/services/bp_rollups.py` |
| Bolt রুট রেজিস্ট্রেশন | `config/api.py` |
| ওয়্যারহাউজ API | `apps/warehouse/api/views.py` |
| ফ্রন্ট ওয়্যারহাউজ UI | `frontend/src/pages/warehouse/` |

চেকলিস্ট আপডেট করতে হলে PR-এ এই ফাইলটিই এডিট করো।
