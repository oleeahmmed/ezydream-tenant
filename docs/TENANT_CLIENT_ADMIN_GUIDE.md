# Ezydream ERP — Tenant & admin (practical guide)

**বাংলা হাতে-কলমে গাইড (দুই ক্লায়েন্ট পর্যন্ত ধাপে ধাপে): [`TENANT_CLIENT_ADMIN_GUIDE_BN.md`](TENANT_CLIENT_ADMIN_GUIDE_BN.md)**

This document explains **what lives in one Django app (`apps.core`)**, how **admin + Unfold** fit in, and **exactly what you click to onboard a client** under `django-tenants`.

---

## 1. Why only `apps.core` (and where “tenant business” goes)

- **`apps.core` is in `SHARED_APPS` only** because it defines **`Client`** (tenant row) and **`Domain`** (hostname → tenant). Those tables **must live in the `public` Postgres schema** so the middleware can resolve tenants on every request.

- **`django_tenants` forbids an empty `TENANT_APPS`**. Until you add tenant-specific business apps, this project uses **`django.contrib.contenttypes`** in `TENANT_APPS` so each tenant schema still gets a normal migration baseline. **You do not need a separate placeholder app** like the old `workspace/` package.

- When you add ERP tables that belong **per company**, create e.g. **`apps.orders`**, add models there, and register **`"apps.orders"` inside `TENANT_APPS`** only (and run migrations). Never put those models in the same app as **`Client` / `Domain`** unless you really know how shared vs tenant splits work.

---

## 2. Two “planes” of admin use

| Plane | Who uses it | Schema | Purpose |
|-------|-------------|--------|---------|
| **Central admin** | Superusers / staff | `public` | Create tenants, domains, global users |
| **Tenant context** | Same code, different hostname | Tenant schema | Future: company-scoped models listed when request hits that tenant’s domain |

Today, most day‑one work happens in **central admin** on `public`, because tenant definitions are stored there.

---

## 3. Dashboard (Unfold)

The home page at `/admin/` is customized with:

- KPI cards: tenant count, domain count, on‑trial count (`config/dashboard_callback.py`).
- The standard Unfold app list remains below the cards (`templates/admin/index.html`).

---

## 4. Step‑by‑step — onboard one client from admin

### Prerequisites

- PostgreSQL + migrations applied (`python manage.py migrate`).
- A **superuser** (`createsuperuser`).
- For local hostname testing, **`DJANGO_ENV=development`** with `SHOW_PUBLIC_IF_NO_TENANT_FOUND = True`, **or** create a `Domain` row (below).

### A. Create the tenant (`Client`)

1. Sign in to `/admin/`.
2. Go to **Tenant clients** → **Add tenant client**.
3. Fill in:
   - **`schema_name`** — becomes the **Postgres schema name** (lowercase, no spaces; e.g. `acme`).
   - **`Name`** — human label (e.g. `Acme Ltd`).
   - Optional **`On trial` / `Paid until`**.
4. Save.

**What happens technically:** `django-tenants` creates schema `acme` (when `auto_create_schema` is enabled) and applies **tenant migrations** (currently `contenttypes` baseline; your future `TENANT_APPS` apps will sync here too).

### B. Map a hostname (`Domain`)

Still in admin (public schema):

1. Open **Domains** → **Add domain**, **or** use the **Domains** tab when editing the `Client`.
2. Set:
   - **`Domain`** — exactly the host the browser sends (`localhost`, `acme.localhost`, `client.example.com`; no `http://`, no path).
   - **`Is primary`** — at least one domain per tenant should be primary.
   - Link to the **`Client`** (`tenant` FK).

3. Save.

**What happens:** Incoming requests with `Host: <that domain>` attach to the correct schema (`acme`). Admin on the “wrong” hostname will 404 in production if `SHOW_PUBLIC_IF_NO_TENANT_FOUND` is `False`.

### C. Browse as that tenant

- **Official django-tenants behaviour:** [`TenantMainMiddleware`](https://django-tenants.readthedocs.io/en/latest/install.html#basic-settings) routes each request to the tenant schema implied by `Host`. Staff auth tables live on **`public`** after `migrate_schemas --shared`, so open **`/admin/` using your *public* tenant’s primary domain** (e.g. `localhost`), not a customer subdomain like `acme.localhost`, unless you intentionally replicate auth per tenant.
- Use the **same codebase**; only the **hostname** changes for tenant-specific routes (e.g. `/api/auth/` on `acme.localhost`).
- Example hosts file + dev server: map `acme.localhost` → `127.0.0.1`, `Domain` row `acme.localhost` → client `acme`, then open `http://acme.localhost:8000/`.

**Note:** Your **URLconf** is still minimal (`/` → admin redirect). ERP pages will live in tenant routes you add later.

---

## 5. What the client “works on”

Conceptually:

1. **Their data** lives in **their schema** (`acme.*` tables), not in `public`.
2. **`Client` / `Domain` rows** remain in **`public`** — that is the SaaS control plane.
3. **Staff accounts** today are standard Django `User` on `public`. If you need **per‑tenant staff** or SSO, plan a custom user model / membership model (future work).

---

## 6. Common pitfalls

| Problem | Fix |
|---------|-----|
| `No tenant for hostname "…"` | Create a `Domain`, or enable dev `SHOW_PUBLIC_IF_NO_TENANT_FOUND`, or use matching `ALLOWED_HOSTS`. |
| `relation "core_client" does not exist` | Keep **`apps.core` in `SHARED_APPS`**, never tenant‑only. |
| Tenant schema empty except `contenttypes` | Expected until you add **`TENANT_APPS` business apps**. |

---

## 7. Related files

| File | Role |
|------|------|
| `config/settings/base.py` | `SHARED_APPS`, `TENANT_APPS`, multitenant settings |
| `config/unfold_settings.py` | English Unfold UI & sidebar |
| `config/dashboard_callback.py` | Dashboard metrics |
| `apps/core/models.py` | `Client`, `Domain` |
| `apps/core/admin.py` | Unfold `ModelAdmin`, inline domains |
| `templates/admin/index.html` | Dashboard + default Unfold index layout |

For database setup in Bangla, still see `RUN_AND_POSTGRES_BN.md`; this file is the English operator guide.
