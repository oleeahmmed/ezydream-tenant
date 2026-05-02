# Django Tenants — সম্পূর্ণ কনফিগারেশন গাইড (বাংলা)

এই নথি [django-tenants ইনস্টলেশন](https://django-tenants.readthedocs.io/en/latest/install.html) ও [ব্যবহার (Creating a tenant)](https://django-tenants.readthedocs.io/en/latest/use.html) অফিসিয়াল ডকুমেন্টেশনের ধাপগুলো অনুসরণ করে লেখা। এই রিপোজিটরির নির্দিষ্ট নাম (`config`, `apps.core`, `apps.auth`) যেখানে লাগে সেখানে মিলিয়ে নেবে।

---

## ১. কী লাগবে

- **PostgreSQL** — স্কিমা-প্রতি টেন্যান্ট মডেল; ডিফল্ট `ENGINE` হবে `django_tenants.postgresql_backend`।
- **Python ৩.১১+** এবং প্রজেক্ট ডিপেন্ডেন্সি (`django-tenants`, `django`, ইত্যাদি) ইনস্টল।

---

## ২. প্যাকেজ ইনস্টল

অফিসিয়াল উদাহরণ:

```bash
pip install django-tenants
```

এই প্রজেক্টে `pyproject.toml` / `uv` ব্যবহার করলে:

```bash
uv sync
```

---

## ৩. `settings.py` — বেসিক সেটিং (অফিসিয়াল চেকলিস্ট)

নিচেরগুলো **অবশ্যই** থাকতে হবে (বিস্তারিত [Basic Settings](https://django-tenants.readthedocs.io/en/latest/install.html#basic-settings))।

### ৩.১ ডাটাবেজ ইঞ্জিন

```python
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": "...",
        "USER": "...",
        "PASSWORD": "...",
        "HOST": "...",
        "PORT": "5432",
    }
}
```

এই রিপোতে `.env` থেকে `DB_*` ভেরিয়েবল পড়ে `config/settings/base.py` এ একই রকম সাজানো আছে।

### ৩.২ রাউটার

```python
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
```

### ৩.৩ মিডলওয়্যার — সবার উপরে

```python
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    # তারপর security, session, common, csrf, auth, ...
]
```

প্রতিটি রিকোয়েস্টে সঠিক PostgreSQL `search_path` সেট করার জন্য এটা **প্রথম** থাকা চাই।

### ৩.৪ টেমপ্লেট — `request` কনটেক্সট

`TEMPLATES` এর `context_processors` তালিকায় **`django.template.context_processors.request`** থাকতে হবে, না হলে টেন্যান্ট `request` এ ঠিকমতো পাওয়া যাবে না।

### ৩.৫ `SHARED_APPS` ও `TENANT_APPS`

- **`SHARED_APPS`**: যেসব অ্যাপ শুধু **`public`** স্কিমায় মাইগ্রেট হবে। এখানে **`django_tenants`**, টেন্যান্ট মডেলের অ্যাপ (এই রিপোতে **`apps.core`**), `contenttypes`, `auth`, `sessions`, `admin`, ইত্যাদি।
- **`TENANT_APPS`**: প্রতিটি টেন্যান্ট স্কিমায় যাবে। খালি রাখা যায় না; এখানে **`django.contrib.contenttypes`** ও **`apps.auth`** (`AUTH_USER_MODEL` = **`tenant_auth.User`**)।

```python
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]
```

### ৩.৬ টেন্যান্ট মডেল পথ

```python
TENANT_MODEL = "core.Client"
TENANT_DOMAIN_MODEL = "core.Domain"
```

(অ্যাপ লেবেল `core` — `apps.core` মডিউল।)

### ৩.৭ (ঐচ্ছিক) `PUBLIC_SCHEMA_URLCONF`

পাবলিক স্কিমা ও টেন্যান্ট স্কিমায় **আলাদা URLconf** চাইলে সেট করা হয়। এই রিপোতে `ROOT_URLCONF` ও `PUBLIC_SCHEMA_URLCONF` দুটোই `config.urls` — সরল সেটআপ।

### ৩.৮ (ডেভেলপমেন্ট) `SHOW_PUBLIC_IF_NO_TENANT_FOUND`

[Other settings](https://django-tenants.readthedocs.io/en/latest/use.html#other-settings): ডোমেইন ম্যাপ না পেলে ডিফল্টে ৪০৪; `True` দিলে পাবলিক স্কিমা দেখাবে। `config/settings/development.py` এ ডেভের জন্য `True`।

---

## ৪. টেন্যান্ট ও ডোমেইন মডেল

অফিসিয়াল নিয়ম: মডেল **`TenantMixin`** ও **`DomainMixin`** থেকে উত্তরাধিকার নেবে। এই প্রজেক্টে `apps/core/models.py` এ `Client` ও `Domain` আছে। অ্যাডমিনে `Client` এর জন্য **`TenantAdminMixin`** ব্যবহার করা হয়েছে ([Admin Support](https://django-tenants.readthedocs.io/en/latest/install.html#admin-support))।

---

## ৫. প্রথম মাইগ্রেশন — শুধু `public`

খালি ডাটাবেজে বা প্রথম সেটআপে:

```bash
python manage.py migrate_schemas --shared
```

এতে **`SHARED_APPS`** এর টেবিলগুলো **`public`** স্কিমায় তৈরি হবে।

> সতর্কতা: সাধারণ `migrate` চালালে শেয়ার্ড ও টেন্যান্ট উভয় স্কিমায় প্রভাব ফেলতে পারে — অফিসিয়াল নোট অনুযায়ী `migrate_schemas` ব্যবহার করাই নিয়ম।

`makemigrations` এর পর আবার `--shared` দরকার হতে পারে।

---

## ৬. `public` টেন্যান্ট ও প্রথম ডোমেইন (অবশ্যকীয়)

[Creating a Tenant](https://django-tenants.readthedocs.io/en/latest/use.html#creating-a-tenant) অনুযায়ী **প্রথমেই** `schema_name='public'` টেন্যান্ট তৈরি করতে হয়, তারপর সেই টেন্যান্টের জন্য **অন্তত একটি `Domain`** (প্রাইমারি)।

সংক্ষিপ্ত ধারণা (ফিল্ড নাম তোমার `Client` মডেলের সাথে মিলিয়ে নেবে):

1. `Client` সেভ: `schema_name='public'`, বাকি বাধ্যতামূলক ফিল্ড (`name`, `paid_until`, `on_trial`, …) পূরণ।
2. `Domain` সেভ: `domain` = ব্রাউজার যে হোস্ট পাঠাবে (**পোর্ট বা `www` ছাড়া**); লোকালে সাধারণত `localhost`। `tenant` = ওই `Client`, `is_primary=True`।

**স্টাফ অ্যাডমিন (`/admin/`)** ও **`django.contrib.auth`** টেবিল **`public`** এ থাকে। তাই অ্যাডমিন ব্রাউজ করার সময় **`Host`** এমন হওয়া উচিত যেটা **`public` টেন্যান্টের ডোমেইন** — সাধারণত `localhost` বা তোমার মূল সাইটের ডোমেইন। গ্রাহকের সাবডোমেইন (`acme.localhost`) দিয়ে `/admin/` খুললে রিকোয়েস্ট **টেন্যান্ট স্কিমায়** যাবে; সেখানে `auth_user` না থাকলে লগইন ভেঙে যেতে পারে — এটা অফিসিয়াল `TenantMainMiddleware` আচরণ।

---

## ৭. আসল গ্রাহক টেন্যান্ট তৈরি

উদাহরণ: `schema_name='acme'`, তারপর `Domain.domain='acme.localhost'`, `is_primary=True`, `tenant` = `acme` ক্লায়েন্ট।

`Client.save()` এর পর সাধারণত স্কিমা তৈরি ও সিঙ্ক হয় (`auto_create_schema=True` থাকলে)।

---

## ৮. সব টেন্যান্টে মাইগ্রেশন

```bash
python manage.py migrate_schemas
```

এতে **`TENANT_APPS`** (যেমন `apps.auth`) এর মাইগ্রেশন **প্রতিটি টেন্যান্ট স্কিমায়** চলবে। নির্দিষ্ট স্কিমায়:

```bash
python manage.py migrate_schemas --schema=acme
```

অপশনের তালিকা: `migrate_schemas --list`।

---

## ৯. ডেভেলপমেন্ট হোস্ট

[Running in Development](https://django-tenants.readthedocs.io/en/latest/use.html#running-in-development): **`.localhost` TLD** ব্রাউজারে লোকাল মেশিনে নিয়ে আসে — `acme.localhost`, `globex.localhost` ইত্যাদি ব্যবহার করা যায়।

`ALLOWED_HOSTS` এ সেই হোস্টগুলো যোগ করতে হবে (এই রিপোতে `.env` এর `DJANGO_ALLOWED_HOSTS`)।

---

## ১০. এই রিপোর সাথে মিলিয়ে নেওয়ার চেকলিস্ট

| বিষয় | অবস্থান |
|--------|---------|
| সেটিংস | `config/settings/base.py`, `development.py`, `production.py` |
| টেন্যান্ট মডেল | `apps/core/models.py` |
| অ্যাডমিন | `apps/core/admin.py` (`TenantAdminMixin` + `Client`) |
| গ্রাহক API (টেন্যান্ট স্কিমায়) | `apps/auth/`, URL ` /api/auth/…` |
| Django-Bolt (ঐচ্ছিক সার্ভার) | `python manage.py runbolt` — রুট API `config/api.py` |

আরও অপারেটর-নির্দেশিকা: `docs/TENANT_CLIENT_ADMIN_GUIDE_BN.md`।

---

## ১১. দরকারি কমান্ড (অফিসিয়াল সারাংশ)

| কাজ | কমান্ড |
|-----|---------|
| শুধু পাবলিক | `migrate_schemas --shared` |
| সব টেন্যান্ট | `migrate_schemas` |
| এক স্কিমায় শেল/কমান্ড | `tenant_command` / `--schema` ([Management commands](https://django-tenants.readthedocs.io/en/latest/use.html#management-commands)) |
| টেন্যান্ট সুপারইউজার | `create_tenant_superuser --schema=...` |

---

## ১২. স্কিমা কনটেক্সট (কোড থেকে)

`django_tenants.utils.schema_context` / `tenant_context` দিয়ে নির্দিষ্ট স্কিমায় কোয়েরি চালানো যায় — বিস্তারিত [Utils](https://django-tenants.readthedocs.io/en/latest/use.html#utils)।

---

**সার:** PostgreSQL + `TenantSyncRouter` + সবার উপরে **`TenantMainMiddleware`** + `SHARED_APPS` / `TENANT_APPS` + **`migrate_schemas --shared`** + **`public` টেন্যান্ট ও ডোমেইন** + বাকি টেন্যান্ট ও **`migrate_schemas`** — এটাই django-tenants এর মূল ইনস্টল ও ব্যবহারের সোজা পথ।

---

## Django-Bolt (API)

টেন্যান্ট গ্রাহক অথ API ও `runbolt` কনফিগের জন্য **`docs/DJANGO_BOLT_SETUP_BN.md`** ও **`docs/DJANGO_BOLT_AUTH_API_BN.md`** দেখো।
