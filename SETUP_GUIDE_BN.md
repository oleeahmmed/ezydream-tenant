# Django Multitenant Setup (Scratch to Professional)  
## বাংলা হাতে-কলমে সম্পূর্ণ ডকুমেন্ট

এই ডকুমেন্ট একদম শুরু থেকে ধরে ধরে লেখা: কেন কোন টুল লাগছে, কোন ফাইল কেন বানানো হয়েছে, কীভাবে run করবেন, কীভাবে dev/production settings switch করবেন, এবং `core` app + `django-tenants` এর বাস্তব প্রয়োগ কী।

---

## ১) প্রজেক্টের লক্ষ্য (আপনার চাহিদা)

আপনার রিকোয়ারমেন্ট ছিল:

1. `uv` ব্যবহার করে virtual environment এবং dependency management  
2. Django project  
3. Dependency: `django`, `django-bolt`, `python-dotenv`, `pillow`, `argon2-cffi`, `django-tenants`, `django-unfold`  
4. সব app `apps/` ফোল্ডারের ভিতরে  
5. settings আলাদা ও clean: `base`, `development`, `production`  
6. `.env` বদলালে environment অনুযায়ী settings switch  
7. professional, clean structure  
8. বাংলায় step-by-step markdown guide

এই ফাইলটি সেই সবকিছুই cover করে।

---

## ২) কেন `core` app বানানো হলো?

`core` app একটি foundational app, যেখানে platform-level shared model/logic রাখা হয়।

### কেন দরকার:

- Multitenant setup এ tenant model (`Client`) এবং domain model (`Domain`) কোথাও রাখতে হয়  
- Authentication, common utilities, shared admin config ইত্যাদি সাধারণত `core` app-এ রাখা হয়  
- ভবিষ্যতে `users`, `billing`, `sales`, `inventory` ইত্যাদি app আলাদা করলেও `core` stable থাকে

### সংক্ষেপে:
`core` হলো project backbone app।

---

## ৩) কেন `django-tenants` ব্যবহার?

`django-tenants` PostgreSQL schema-based multitenancy সহজ করে:

- এক database, একাধিক tenant schema  
- প্রতিটি client/tenant এর data isolate থাকে  
- domain/subdomain দিয়ে tenant resolve হয়  
- SaaS ERP সিস্টেমে multi-company support এর জন্য ideal

### গুরুত্বপূর্ণ:
এই প্রজেক্টে `django-tenants` বসানো আছে—**ডেভ ও প্রোড দুজায়ই PostgreSQL ব্যতীত সাধারণত চলবে না** (এবং `migrate` এর জন্য টেন্যান্ট ডাটাবেজ ব্যাকএন্ড `set_schema` API লাগে)। SQLite কেবল ডকুমেন্টেশন থেকে লোকেশন খুঁজে টেন্যান্ট ডেভ সিমুলেট করা যাবে না; বিস্তারিত [RUN_AND_POSTGRES_BN.md](RUN_AND_POSTGRES_BN.md)।

---

## ৪) পুরো setup কমান্ড (Scratch থেকে)

> নিচের ধাপগুলো নতুন machine/clean folder থেকে follow করুন।

### ধাপ ০: `uv` install

Linux/macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

চেক:

```bash
uv --version
```

### ধাপ ১: project folder

```bash
mkdir ezydream-erp-multitanant
cd ezydream-erp-multitanant
```

### ধাপ ২: virtual environment (`uv`)

```bash
uv venv .venv
source .venv/bin/activate
```

### ধাপ ৩: dependency install

```bash
uv pip install django django-bolt python-dotenv pillow argon2-cffi django-tenants django-unfold psycopg2-binary
```

### ধাপ ৪: django project bootstrap

```bash
uv run django-admin startproject config .
```

### ধাপ ৫: apps folder architecture

```bash
mkdir -p apps
touch apps/__init__.py
uv run python manage.py startapp core apps/core
```

---

## ৫) Professional folder structure (Final)

```text
ezydream-erp-multitanant/
├── .env
├── .env.example
├── .gitignore
├── manage.py
├── pyproject.toml
├── apps/
│   ├── __init__.py
│   └── core/          # SHARED_APPS: Tenant model (Client / Domain)
└── config/
    ├── __init__.py
    ├── asgi.py
    ├── urls.py
    ├── wsgi.py
    └── settings/
        ├── __init__.py
        ├── base.py
        ├── development.py
        └── production.py
```

---

## ৬) Settings split কীভাবে কাজ করে?

### `config/settings/base.py`

এখানে common config:

- `INSTALLED_APPS` (`django-unfold`, `django-tenants`, `apps.core`, contrib apps …) · `TENANT_APPS` uses e.g. `django.contrib.contenttypes` for tenant-schema migrations  
- middleware (`TenantMainMiddleware`)  
- database/env পড়া  
- static/media  
- password hasher (Argon2)

### `config/settings/development.py`

- `from .base import *`  
- `DEBUG = True`

### `config/settings/production.py`

- `from .base import *`  
- `DEBUG = False`  
- SSL/cookie security flags enabled

### `config/settings/__init__.py`

`DJANGO_ENV` পড়ে decide করে:

- `production` হলে production settings  
- অন্য সব ক্ষেত্রে development settings

---

## ৭) `.env` driven environment switching

`.env` example:

```env
DJANGO_ENV=development
DJANGO_SECRET_KEY=django-insecure-local-dev-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django_tenants.postgresql_backend
DB_NAME=ezydream_erp
DB_USER=ezydream_user
DB_PASSWORD=your-strong-password-here
DB_HOST=127.0.0.1
DB_PORT=5432
TIME_ZONE=Asia/Dhaka
```

Production এ গেলে:

```env
DJANGO_ENV=production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django_tenants.postgresql_backend
DB_NAME=erp_db
DB_USER=erp_user
DB_PASSWORD=strong_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

---

## ৮) Step-8 এর সব কাজ: বিস্তারিত code সহ (হাতে-কলমে)

এই অংশটাই তোমার চাওয়া মূল অংশ: `django-tenants + django-unfold + Argon2 + env-driven settings` কীভাবে বসানো হয়েছে, পুরো code সহ।

### ৮.১ `apps/core/apps.py` (App path fix)

**কেন:** app যেহেতু `apps/core` ফোল্ডারে, তাই Django app name হবে `apps.core`।

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
```

---

### ৮.২ `apps/core/models.py` (Tenant model + Domain model)

**কেন:** `django-tenants` এ tenant identify করতে `TenantMixin` এবং domain resolve করতে `DomainMixin` model লাগে।

```python
from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Client(TenantMixin):
    name = models.CharField(max_length=120)
    paid_until = models.DateField(null=True, blank=True)
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass
```

---

### ৮.৩ `apps/core/admin.py` (Admin registration)

**কেন:** tenant/domain object admin panel থেকে manage করার জন্য register করা হয়।

```python
from django.contrib import admin
from .models import Client, Domain

admin.site.register(Client)
admin.site.register(Domain)
```

---

### ৮.৪ `config/settings/base.py` (Step-8 এর মূল configuration)

**কেন এই ফাইলটি সবচেয়ে গুরুত্বপূর্ণ:**  
এখানেই `django-tenants`, `unfold`, `.env`, Argon2, middleware, DB router সব একসাথে configure হয়েছে।

```python
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]

SHARED_APPS = [
    "django_tenants",
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # `TENANT_MODEL` / `Domain` যেখানে — সেই অ্যাপ public স্কিমায় (SHARED_APPS)
    "apps.core",
]

# `TENANT_APPS` cannot be empty. Use a tenant-only contrib app bundle (often `contenttypes`).
TENANT_APPS = [
    "django.contrib.contenttypes",
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = "core.Client"
TENANT_DOMAIN_MODEL = "core.Domain"

MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": os.getenv(
            "DB_ENGINE",
            "django_tenants.postgresql_backend",
        ),
        "NAME": os.getenv("DB_NAME", "ezydream_erp"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
```

---

### ৮.৫ `config/settings/__init__.py` (Environment switch engine)

**কেন:** `DJANGO_ENV` বদলালেই settings source বদলে যাবে।

```python
import os

env = os.getenv("DJANGO_ENV", "development").lower()

if env == "production":
    from .production import *  # noqa: F403, F401
else:
    from .development import *  # noqa: F403, F401
```

---

### ৮.৬ `config/settings/development.py`

```python
from .base import *  # noqa: F403, F401

DEBUG = True
```

### ৮.৭ `config/settings/production.py`

```python
from .base import *  # noqa: F403, F401

DEBUG = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

### ৮.৮ `.env` (development)

```env
DJANGO_ENV=development
DJANGO_SECRET_KEY=django-insecure-local-dev-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django_tenants.postgresql_backend
DB_NAME=ezydream_erp
DB_USER=ezydream_user
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=5432
TIME_ZONE=Asia/Dhaka
```

### ৮.৯ `.env.example` (template)

```env
DJANGO_ENV=development
DJANGO_SECRET_KEY=change-me-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django_tenants.postgresql_backend
DB_NAME=ezydream_erp
DB_USER=ezydream_user
DB_PASSWORD=your-strong-password-here
DB_HOST=127.0.0.1
DB_PORT=5432

TIME_ZONE=Asia/Dhaka
```

---

### ৮.১০ `pyproject.toml` (uv dependency declaration)

```toml
[project]
name = "ezydream-erp-multitenant"
version = "0.1.0"
description = "Professional Django multitenant starter setup"
requires-python = ">=3.11"
dependencies = [
    "django",
    "django-bolt",
    "python-dotenv",
    "pillow",
    "argon2-cffi",
    "django-tenants",
    "django-unfold",
    "psycopg2-binary",
]

[tool.uv]
dev-dependencies = []
```

---

## ৯) `django-unfold` কীভাবে যুক্ত হলো?

`base.py` এ `unfold` `INSTALLED_APPS`-এ যোগ করা হয়েছে যাতে Django admin UI modern look পায়।  
আপনি চাইলে next step এ unfold branding/theme customization আলাদা করে যুক্ত করতে পারেন।

---

## ১০) প্রথমবার run (practical hands-on)

**PostgreSQL আগে থেকেই ও `.env`-এ ডাটাবেজ ক্ষেত্র ভরাট করতে হবে।** এরপরের সব ট্রoubleshooting ও সার্ভিস চেক [RUN_AND_POSTGRES_BN.md](RUN_AND_POSTGRES_BN.md)।

```bash
source .venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin panel:

- URL: `http://127.0.0.1:8000/admin/`

---

## পরবর্তী সব ধাপ কোথায়?

ধাপ **১০** এর পরের সবকিছু—PostgreSQL লাগবে কিনা, `venv` অ্যাক্টিভ করে `migrate/runserver`, আপনার মেশিনে ইতিমধ্যে PostgreSQL আছে এমন ক্ষেত্রে করণীয়, error/troubleshooting, আমাদের environment এ করা চেষ্টার ফল—সব **[RUN_AND_POSTGRES_BN.md](RUN_AND_POSTGRES_BN.md)** ফাইলে বিস্তারিত লেখা হয়েছে।

**এক লাইনে মনে রাখা:** এই স্ট্যাকে `django-tenants` = **PostgreSQL**; এরপরের বাস্তব run সব উপরের নতুন ডক থেকে ফলো করুন।
