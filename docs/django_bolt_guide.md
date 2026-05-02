# Django-Bolt দিয়ে Sales API — একদম হাতে-কলমে সম্পূর্ণ গাইড

> **বাংলায় লেখা**, একদম Beginner থেকে শুরু করে Production-ready API পর্যন্ত।  
> প্রতিটি কমান্ড, প্রতিটি কোড লাইন, প্রতিটি concept বিস্তারিত ব্যাখ্যা সহ।

---

## 📋 সূচিপত্র

1. [Django-Bolt কী এবং কেন?](#১-django-bolt-কী-এবং-কেন)
2. [System Requirements](#২-system-requirements)
3. [Virtual Environment তৈরি ও Activate](#৩-virtual-environment-তৈরি-ও-activate)
4. [Dependencies Install](#৪-dependencies-install)
5. [Django Project তৈরি](#৫-django-project-তৈরি)
6. [Settings Configure করা](#৬-settings-configure-করা)
7. [ASGI Configure করা](#৭-asgi-configure-করা)
8. [Models তৈরি (Database Structure)](#৮-models-তৈরি-database-structure)
9. [Serializers তৈরি (Data Validation)](#৯-serializers-তৈরি-data-validation)
10. [Auth Endpoints তৈরি (Login, Register)](#১০-auth-endpoints-তৈরি-login-register)
11. [ViewSet দিয়ে Product API](#১১-viewset-দিয়ে-product-api)
12. [ViewSet দিয়ে Sales Order API](#১২-viewset-দিয়ে-sales-order-api)
13. [Migration ও Server চালু করা](#১৩-migration-ও-server-চালু-করা)
14. [API Test করা (curl দিয়ে)](#১৪-api-test-করা-curl-দিয়ে)
15. [সম্পূর্ণ Concept Summary](#১৫-সম্পূর্ণ-concept-summary)

---

## ১. Django-Bolt কী এবং কেন?

### Django REST Framework (DRF) এর সাথে পার্থক্য

তুমি হয়তো DRF চেনো। Django-Bolt একটি নতুন framework যেটা DRF এর মতো কাজ করে কিন্তু অনেক দিক থেকে আলাদা:

| বিষয় | Django REST Framework | Django-Bolt |
|------|----------------------|-------------|
| Architecture | WSGI (sync) | ASGI (async) |
| View style | Class-based, function-based | Function + Class-based ViewSet |
| Routing | `urls.py` তে manually | Auto-discovery (`api.py`) |
| Validation | Serializer class | `msgspec.Struct` ভিত্তিক Serializer |
| Auth | Token, Session, JWT (third-party) | Built-in JWT (Rust-এ runs) |
| Performance | Moderate | High (Rust layer আছে) |
| Type hints | Optional | Required (strict typing) |

### Django-Bolt এর মূল Architecture

```
HTTP Request আসলো
       ↓
  Rust Layer (Bolt)
  ├── JWT token validate করে (database hit ছাড়া)
  ├── Permission guard চেক করে
  └── Route match করে
       ↓
  Python Handler (async)
  ├── তোমার business logic
  ├── Django ORM (async) দিয়ে DB access
  └── Response return করো
       ↓
HTTP Response যাবে
```

**কেন Rust layer?**  
JWT validation, permission check — এগুলো প্রতিটি request-এ করতে হয়। Rust এ করলে Python GIL এর বাধা নেই, অনেক দ্রুত।

---

## ২. System Requirements

কমান্ড দিয়ে চেক করো সব আছে কিনা:

```bash
# Python version চেক করো (3.11+ লাগবে)
python --version
# অথবা
python3 --version

# pip আছে কিনা চেক করো
pip --version

# git আছে কিনা (optional, কিন্তু ভালো অভ্যাস)
git --version
```

**Expected output:**
```
Python 3.11.x   ← এইরকম কিছু দেখাবে
pip 23.x.x
git version 2.x.x
```

Python না থাকলে: https://www.python.org/downloads/ থেকে ডাউনলোড করো।

---

## ৩. Virtual Environment তৈরি ও Activate

### Virtual Environment কী?

ধরো তোমার কম্পিউটারে দুটো project আছে:
- Project A → Django 4.2 লাগে
- Project B → Django 5.0 লাগে

দুটো একসাথে globally install করলে conflict হবে। Virtual Environment হলো একটা isolated folder যেখানে প্রতিটি project এর নিজস্ব Python packages থাকে।

```
আমার Computer
├── Python (global)
├── venv_project_a/     ← Project A এর isolated environment
│   └── lib/
│       └── django==4.2
└── venv_project_b/     ← Project B এর isolated environment
    └── lib/
        └── django==5.0
```

### Step 1: Project Folder তৈরি করো

```bash
# Desktop বা যেকোনো জায়গায় folder তৈরি করো
mkdir sales_project
cd sales_project

# এখন তুমি sales_project folder এর ভেতরে আছো
# pwd কমান্ড দিয়ে দেখো কোথায় আছো
pwd
```

**Output দেখাবে:**
```
/home/তোমার-নাম/sales_project
```

### Step 2: Virtual Environment তৈরি করো

```bash
# "venv" নামে একটি virtual environment তৈরি করো
python -m venv venv

# Windows এ হয়তো python3 লাগবে:
# python3 -m venv venv
```

এই কমান্ড দেওয়ার পর `venv` নামে একটি folder তৈরি হবে:

```
sales_project/
└── venv/               ← এটা তৈরি হলো
    ├── bin/            (Linux/Mac)
    │   ├── python
    │   ├── pip
    │   └── activate    ← এই script দিয়ে activate করবো
    └── Scripts/        (Windows)
        ├── python.exe
        ├── pip.exe
        └── activate    ← Windows এ এইটা
```

### Step 3: Virtual Environment Activate করো

**Linux / Mac:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Activate হয়েছে কিনা বুঝবো কীভাবে?**

Terminal prompt এ `(venv)` দেখাবে:
```
(venv) user@computer:~/sales_project$
```

ঐ `(venv)` টুকু মানে তুমি এখন virtual environment এর ভেতরে আছো।

**Important:** প্রতিবার নতুন terminal খুললে আবার activate করতে হবে!

### Deactivate করতে চাইলে:
```bash
deactivate
```

---

## ৪. Dependencies Install

### requirements.txt তৈরি করো

```bash
# sales_project folder এর ভেতরে এই ফাইলটি তৈরি করো
# nano অথবা যেকোনো text editor দিয়ে
nano requirements.txt
```

নিচের content লিখে save করো:

```
django>=4.2
django-bolt
PyJWT
```

**প্রতিটি package কী করে:**
- `django>=4.2` → Django web framework (4.2 বা তার উপরের version)
- `django-bolt` → আমাদের মূল framework
- `PyJWT` → JWT token তৈরি ও validate করার জন্য

### Install করো:

```bash
pip install -r requirements.txt
```

**Output দেখবে (এরকম কিছু):**
```
Collecting django>=4.2
  Downloading Django-5.0.4-py3-none-any.whl (8.1 MB)
Collecting django-bolt
  Downloading django_bolt-0.x.x-py3-none-any.whl
Collecting PyJWT
  Downloading PyJWT-2.x.x-py3-none-any.whl
Installing collected packages: ...
Successfully installed django-5.0.4 django-bolt-0.x.x PyJWT-2.x.x
```

**ঠিকমতো install হয়েছে কিনা চেক করো:**

```bash
pip list
```

Output এ django, django-bolt, PyJWT দেখাবে।

---

## ৫. Django Project তৈরি

### Django Project আর Django App এর পার্থক্য

অনেকে এই দুটো নিয়ে confused হয়:

```
sales_project/          ← এটা Django PROJECT (পুরো application)
├── sales_project/      ← এটা project configuration folder
│   ├── settings.py     ← সব settings এখানে
│   ├── urls.py         ← Django admin URL
│   └── asgi.py         ← Server entry point
└── sales/              ← এটা Django APP (একটি feature module)
    ├── models.py        ← Database tables
    └── api.py           ← API endpoints
```

**Project** = পুরো website/application  
**App** = একটি নির্দিষ্ট feature (যেমন: sales, blog, users)

### Step 1: Django Project তৈরি করো

```bash
# নিশ্চিত করো তুমি sales_project folder এ আছো
# এবং venv activate আছে

django-admin startproject sales_project .
```

**গুরুত্বপূর্ণ:** শেষে `.` (dot) দিতে হবে। এটা মানে "current folder এ তৈরি করো"।

dot না দিলে:
```
sales_project/
└── sales_project/      ← extra nested folder হয়ে যাবে
    └── sales_project/
```

dot দিলে (সঠিক):
```
sales_project/          ← তোমার project folder (এখানেই আছো)
├── manage.py           ← Django management tool
└── sales_project/      ← configuration folder
    ├── settings.py
    ├── urls.py
    └── asgi.py
```

### Step 2: Sales App তৈরি করো

```bash
python manage.py startapp sales
```

এখন folder structure এরকম হবে:

```
sales_project/
├── manage.py
├── requirements.txt
├── venv/
├── sales_project/          ← project config
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py             ← এটা delete করবো
│   └── asgi.py
└── sales/                  ← আমাদের sales app
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py           ← এখানে কাজ করবো
    ├── tests.py
    ├── views.py            ← এটা delete করবো (bolt use করবো)
    └── migrations/
        └── __init__.py
```

---

## ৬. Settings Configure করা

`sales_project/settings.py` ফাইলটি খোলো। এটাই Django এর central configuration।

```bash
nano sales_project/settings.py
```

### পুরো settings.py replace করো এইটা দিয়ে:

```python
"""
Sales Project — Django Settings
================================
Django-Bolt দিয়ে বানানো Sales API এর সব configuration এখানে।
"""

from pathlib import Path

# BASE_DIR মানে হলো আমাদের project এর root folder
# __file__ = এই settings.py ফাইলের path
# .parent = settings.py এর parent folder (sales_project/)
# .parent.parent = তার parent (root sales_project/)
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY: Django internally এটা cryptographic operations এ ব্যবহার করে
# Production এ অবশ্যই environment variable থেকে নিতে হবে
# os.environ.get("SECRET_KEY") দিয়ে
SECRET_KEY = "django-insecure-change-this-in-production-pleeeease"

# DEBUG=True মানে error page বিস্তারিত দেখাবে — শুধু development এ
DEBUG = True

# কোন host থেকে request accept করবে
# Development এ ["*"] ঠিক আছে, production এ specific domain দিতে হবে
ALLOWED_HOSTS = ["*"]

# ── Installed Apps ────────────────────────────────────────────────────────────
# Django কোন apps ব্যবহার করবে তার list
INSTALLED_APPS = [
    # Django built-in apps
    "django.contrib.admin",         # Admin panel
    "django.contrib.auth",          # User authentication system
    "django.contrib.contenttypes",  # Content type framework
    "django.contrib.sessions",      # Session management
    "django.contrib.messages",      # Flash messages
    "django.contrib.staticfiles",   # Static files (CSS, JS, images)

    # Third-party: Django-Bolt framework
    "django_bolt",

    # আমাদের নিজের sales app
    "sales",
]

# Middleware গুলো প্রতিটি request/response এ chain হিসেবে কাজ করে
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sales_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Django-Bolt ASGI ব্যবহার করে, তাই ASGI_APPLICATION দিতে হবে
# wsgi.py নয়!
ASGI_APPLICATION = "sales_project.asgi.application"

# ── Database ──────────────────────────────────────────────────────────────────
# Development এ SQLite ব্যবহার করছি (কোনো setup লাগে না)
# Production এ PostgreSQL recommend করা হয়
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # db.sqlite3 ফাইলে সব data থাকবে
    }
}

# ── Password Validation ───────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ── Localization ──────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Dhaka"    # Bangladesh timezone
USE_I18N = True
USE_TZ = True               # Timezone-aware datetime use করবো

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ── Django-Bolt Global Auth & Permission ─────────────────────────────────────
# এটাই সবচেয়ে গুরুত্বপূর্ণ part!
#
# এই দুটো setting মানে:
#   1. সব endpoint এ automatically JWT token চেক হবে
#   2. সব endpoint এ login required থাকবে
#
# কোনো endpoint public করতে চাইলে সেখানে explicitly
# guards=[AllowAny()] দিতে হবে (যেমন: login, register endpoint)
from django_bolt.auth import JWTAuthentication, IsAuthenticated  # noqa: E402

BOLT_AUTHENTICATION_CLASSES = [
    JWTAuthentication(),
]

BOLT_DEFAULT_PERMISSION_CLASSES = [
    IsAuthenticated(),
]
```

### Settings এর Key Points:

**`INSTALLED_APPS` তে কেন `django_bolt` add করতে হয়?**  
Django কে জানাতে হয় যে এই package ব্যবহার করবো। তা না হলে Django Bolt এর management commands, auto-discovery — কিছুই কাজ করবে না।

**`ASGI_APPLICATION` কেন?**  
Django-Bolt একটি ASGI framework। ASGI মানে Asynchronous Server Gateway Interface। Traditional Django WSGI (synchronous) ব্যবহার করে। কিন্তু async code লিখতে হলে ASGI লাগবে।

**`BOLT_AUTHENTICATION_CLASSES` এবং `BOLT_DEFAULT_PERMISSION_CLASSES` কী?**  
এই দুটো globally set করা মানে প্রতিটি API endpoint এ by default:
- JWT token validate হবে (`BOLT_AUTHENTICATION_CLASSES`)
- Login required থাকবে (`BOLT_DEFAULT_PERMISSION_CLASSES`)

---

## ৭. ASGI Configure করা

`sales_project/asgi.py` ফাইলটি খোলো এবং এভাবে লিখো:

```python
"""
ASGI Configuration
==================
Django-Bolt একটি ASGI framework। Server চালু হওয়ার সময়
এই ফাইল দিয়ে application load হয়।

WSGI (old):  sync, একটা request process হওয়ার সময় thread block হয়
ASGI (new):  async, multiple requests একসাথে handle করতে পারে
"""

import os

from django.core.asgi import get_asgi_application

# Django কে বলছি কোথায় settings আছে
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sales_project.settings")

# Django এর ASGI application object তৈরি করো
application = get_asgi_application()
```

### urls.py update করো:

`sales_project/urls.py` খোলো:

```python
"""
Django URL Configuration

Django-Bolt নিজেই সব API route handle করে (auto-discovery)।
আমাদের urls.py তে শুধু Django admin route রাখলেই চলে।

Auto-discovery কীভাবে কাজ করে:
  Django-Bolt automatically প্রতিটি installed app এর
  api.py ফাইল খোঁজে এবং সব route merge করে।

  sales_project/api.py → /api/health, /api/auth/...
  sales/api.py         → /api/products, /api/orders
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

---

## ৮. Models তৈরি (Database Structure)

Model হলো তোমার database table এর Python representation।  
`sales/models.py` ফাইলটি খোলো এবং পুরোটা replace করো:

```python
"""
Sales App Models
================

আমাদের database এ ৩টি table থাকবে:

  Product        → পণ্যের তথ্য
  SalesOrder     → একটি order (customer + items)
  SalesOrderItem → প্রতিটি order এর line item (কোন product, কত qty)

Relationship:
  SalesOrder ──── many-to-one ──→ User (Django built-in)
  SalesOrderItem ─ many-to-one ──→ SalesOrder
  SalesOrderItem ─ many-to-one ──→ Product

ছবিতে:
  User
   │
   └── SalesOrder (customer=User)
          │
          ├── SalesOrderItem (product=Product, qty=2)
          └── SalesOrderItem (product=Product, qty=1)
"""

from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    """
    বিক্রয়যোগ্য পণ্য।

    Django Model এর প্রতিটি field = database এর একটি column।
    """

    # CharField → VARCHAR type column, max_length অবশ্যই দিতে হবে
    name = models.CharField(max_length=255, verbose_name="পণ্যের নাম")

    # TextField → TEXT type column, যতখুশি লম্বা text
    # blank=True মানে form validation এ empty allowed
    description = models.TextField(blank=True, verbose_name="বিবরণ")

    # DecimalField → DECIMAL type, টাকার জন্য Float ব্যবহার করো না!
    # Float এ precision error হয়: 10.1 + 10.2 = 20.299999999...
    # Decimal এ সঠিক: 10.1 + 10.2 = 20.3
    price = models.DecimalField(
        max_digits=12,      # মোট কতটি digit (. এর আগে ও পরে মিলে)
        decimal_places=2,   # দশমিকের পরে কতটি digit
        verbose_name="একক মূল্য (BDT)",
    )

    # PositiveIntegerField → শুধু 0 বা তার বেশি integer
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="মজুদ পরিমাণ",
    )

    # BooleanField → True/False (database এ 0/1)
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়?")

    # auto_now_add=True → record তৈরির সময় automatically current time set হয়
    created_at = models.DateTimeField(auto_now_add=True)

    # auto_now=True → প্রতিবার save হলে automatically current time update হয়
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Default ordering: name অনুযায়ী A-Z সাজাও
        ordering = ["name"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        # Admin panel এ এবং print() করলে এই string দেখাবে
        return f"{self.name} (৳{self.price})"


class SalesOrder(models.Model):
    """
    একটি সম্পূর্ণ বিক্রয় অর্ডার।

    একজন customer একটি order করে।
    Order এর ভেতরে multiple items থাকতে পারে।
    """

    STATUS_CHOICES = [
        # (database তে save হবে, human-readable label)
        ("pending", "Pending — অপেক্ষমাণ"),
        ("confirmed", "Confirmed — নিশ্চিত"),
        ("shipped", "Shipped — পাঠানো হয়েছে"),
        ("delivered", "Delivered — পৌঁছেছে"),
        ("cancelled", "Cancelled — বাতিল"),
    ]

    # ForeignKey → Many-to-One relationship
    # অনেক order → একজন user
    # on_delete=PROTECT মানে user delete করলে error দেবে যদি order থাকে
    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="sales_orders",    # user.sales_orders.all() দিয়ে access করতে পারবো
        verbose_name="Customer",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="অর্ডার স্ট্যাটাস",
    )

    customer_note = models.TextField(blank=True, verbose_name="Customer এর নোট")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # "-" মানে descending (নতুনটা আগে)
        verbose_name = "Sales Order"
        verbose_name_plural = "Sales Orders"

    def __str__(self) -> str:
        return f"Order #{self.pk} — {self.customer.username} ({self.status})"

    @property
    def total_amount(self) -> Decimal:
        """
        সব line item এর মোট টাকা।

        @property decorator মানে এটা method না, attribute হিসেবে access করা যাবে:
        order.total_amount  (parenthesis লাগবে না)
        """
        return sum(
            item.unit_price * item.quantity
            for item in self.items.all()  # related_name="items" দিয়ে access
        )


class SalesOrderItem(models.Model):
    """
    একটি SalesOrder এর একটি line item।

    একটি order এ অনেক item থাকতে পারে।
    প্রতিটি item একটি product কে refer করে।

    কেন unit_price আলাদা save করা হচ্ছে?
    কারণ Product এর price পরে change হতে পারে।
    কিন্তু order করার সময় কত দাম ছিলো সেটা record থাকা দরকার।
    """

    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,   # Order delete হলে items ও delete হবে
        related_name="items",        # order.items.all() দিয়ে access
        verbose_name="অর্ডার",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,   # Product delete করতে পারবে না যদি order থাকে
        related_name="order_items",
        verbose_name="পণ্য",
    )

    quantity = models.PositiveIntegerField(default=1, verbose_name="পরিমাণ")

    # Order করার সময়কার দাম capture করা হচ্ছে
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="একক মূল্য (order এর সময়কার)",
    )

    class Meta:
        verbose_name = "Sales Order Item"
        verbose_name_plural = "Sales Order Items"

    def __str__(self) -> str:
        return f"{self.product.name} × {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        """এই line এর মোট = unit_price × quantity"""
        return self.unit_price * self.quantity
```

### Model এর গুরুত্বপূর্ণ Concepts:

**`on_delete` কী?**

ForeignKey এ `on_delete` বলতে হয় — referenced object delete হলে কী করবে:

```python
# on_delete options:
models.CASCADE   # parent delete → child ও delete হবে
models.PROTECT   # parent delete করতে পারবে না যদি child থাকে (error দেবে)
models.SET_NULL  # parent delete → child এর field null হবে (null=True লাগবে)
models.SET_DEFAULT # parent delete → default value set হবে
```

**`related_name` কী?**

```python
# Product model এ:
order = models.ForeignKey(SalesOrder, related_name="items")

# এখন এভাবে access করতে পারবো:
order = SalesOrder.objects.get(id=1)
items = order.items.all()    # ← related_name="items" use হচ্ছে
```

---

## ৯. Serializers তৈরি (Data Validation)

`sales/serializers.py` নামে নতুন ফাইল তৈরি করো:

```bash
touch sales/serializers.py
nano sales/serializers.py
```

Serializer দুটো কাজ করে:
1. **Input validation**: User যা পাঠিয়েছে সেটা সঠিক কিনা চেক
2. **Output shaping**: Database থেকে data নিয়ে JSON বানাও

```python
"""
Sales App Serializers
=====================

Django-Bolt এর Serializer ক্লাস msgspec.Struct এর উপর বানানো।
DRF এর Serializer থেকে আলাদা:

DRF Serializer:
  class ProductSerializer(serializers.ModelSerializer):
      class Meta:
          model = Product
          fields = ['id', 'name', 'price']

Bolt Serializer:
  class ProductResponse(Serializer):
      id: int
      name: str
      price: float

Bolt এর approach:
  - Type hints mandatory (Python typing system use করে)
  - msgspec এর C implementation → অনেক দ্রুত
  - Input ও Output আলাদা serializer রাখা হয় (single responsibility)
"""

from __future__ import annotations
from decimal import Decimal
from typing import Annotated, Literal
from msgspec import Meta
from django_bolt.serializers import Serializer, field_validator


# ═══════════════════════════════════════════════════════════════════
# PRODUCT SERIALIZERS
# ═══════════════════════════════════════════════════════════════════

class ProductResponse(Serializer):
    """
    Product দেখানোর জন্য Response Serializer।
    Database থেকে Product object নিয়ে এই shape এ JSON বানাবো।

    type annotation মানে:
      id: int      → "id" field থাকবে, integer হতে হবে
      name: str    → "name" field থাকবে, string হতে হবে
    """
    id: int
    name: str
    description: str
    price: float         # Decimal → float (JSON এ Decimal নেই)
    stock_quantity: int
    is_active: bool


class ProductCreateInput(Serializer):
    """
    Product তৈরির জন্য Input Serializer।
    User যা POST করবে তা এই shape এ validate হবে।

    Annotated[type, Meta(...)] দিয়ে constraint দেওয়া হয়:
      Annotated[str, Meta(min_length=1)] → কমপক্ষে ১ character
      Annotated[float, Meta(gt=0)]       → শূন্যের বেশি হতে হবে (gt = greater than)
    """

    name: Annotated[str, Meta(min_length=1, max_length=255)]
    description: str = ""           # default value: empty string
    price: Annotated[float, Meta(gt=0)]
    stock_quantity: Annotated[int, Meta(ge=0)] = 0   # ge = greater than or equal
    is_active: bool = True

    @field_validator("name")
    def clean_name(cls, v: str) -> str:
        """
        field_validator: একটি field এর value validate বা transform করে।

        এখানে: name এর আগে/পরে extra space remove করছি।
        strip() → "  ল্যাপটপ  " → "ল্যাপটপ"
        """
        return v.strip()


class ProductUpdateInput(Serializer):
    """
    Product update এর জন্য Input Serializer।
    সব field optional কারণ partial update করতে পারবে।

    type | None = None মানে:
      - field টা পাঠানো না হলে None হবে (default)
      - পাঠানো হলে validate হবে
    """
    name: Annotated[str, Meta(min_length=1, max_length=255)] | None = None
    description: str | None = None
    price: Annotated[float, Meta(gt=0)] | None = None
    stock_quantity: Annotated[int, Meta(ge=0)] | None = None
    is_active: bool | None = None


# ═══════════════════════════════════════════════════════════════════
# ORDER ITEM SERIALIZERS
# ═══════════════════════════════════════════════════════════════════

class OrderItemResponse(Serializer):
    """একটি order line item এর response।"""
    id: int
    product_id: int
    product_name: str = ""
    quantity: int
    unit_price: float
    line_total: float = 0.0


class OrderItemInput(Serializer):
    """Order তৈরির সময় প্রতিটি item এর input।"""
    product_id: int
    quantity: Annotated[int, Meta(ge=1)]    # কমপক্ষে ১টা order করতে হবে


# ═══════════════════════════════════════════════════════════════════
# SALES ORDER SERIALIZERS
# ═══════════════════════════════════════════════════════════════════

class SalesOrderResponse(Serializer):
    """Order detail response (items সহ)।"""
    id: int
    customer_id: int
    customer_username: str = ""
    status: str
    customer_note: str
    items: list[OrderItemResponse] = []    # nested list of items
    total_amount: float = 0.0


class SalesOrderListResponse(Serializer):
    """Order list এর সংক্ষিপ্ত response (items ছাড়া)।"""
    id: int
    customer_id: int
    status: str
    total_amount: float = 0.0
    created_at: str = ""


class SalesOrderCreateInput(Serializer):
    """
    নতুন order তৈরির input।

    User পাঠাবে:
    {
        "customer_note": "দ্রুত পাঠান",
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 1}
        ]
    }
    """
    customer_note: str = ""
    items: list[OrderItemInput]

    @field_validator("items")
    def must_have_items(cls, v: list) -> list:
        """কমপক্ষে একটি item থাকতে হবে।"""
        if not v:
            raise ValueError("অর্ডারে অন্তত একটি পণ্য থাকতে হবে।")
        return v


class SalesOrderStatusUpdate(Serializer):
    """
    Order status পরিবর্তনের input।

    Literal["a", "b", "c"] মানে শুধু এই values গুলোই allowed।
    অন্য কিছু দিলে automatic validation error।
    """
    status: Literal["pending", "confirmed", "shipped", "delivered", "cancelled"]
```

### Serializer এর গুরুত্বপূর্ণ Concepts:

**`Annotated` এবং `Meta` কী?**

```python
from typing import Annotated
from msgspec import Meta

# Annotated[original_type, extra_metadata]
# Meta দিয়ে constraint দেওয়া হয়

name: Annotated[str, Meta(min_length=1, max_length=100)]
# → str type, কমপক্ষে 1 char, বেশিতে 100 char

price: Annotated[float, Meta(gt=0, le=1000000)]
# → float type, 0 এর বেশি (gt=greater than), 10 লাখের কম বা সমান

age: Annotated[int, Meta(ge=0, le=150)]
# → int type, 0 বা বেশি (ge=greater than or equal), 150 বা কম

# Meta constraints:
# gt  = greater than (strictly)
# ge  = greater than or equal
# lt  = less than (strictly)
# le  = less than or equal
# min_length = string minimum length
# max_length = string maximum length
# pattern    = regex pattern
```

**Input আর Response আলাদা কেন?**

```
User POST করে (Input):         আমরা Response দিই:
{                              {
  "name": "Laptop",              "id": 1,
  "price": 50000,                "name": "Laptop",
  "stock": 10                    "price": 50000,
}                                "stock": 10,
                                 "is_active": true,
                                 "created_at": "2024..."
                               }
```

Input এ `id`, `created_at` দরকার নেই (auto-generate হয়)।  
Response এ সব field দেখাই। তাই আলাদা class রাখা ভালো practice।

---

## ১০. Auth Endpoints তৈরি (Login, Register)

`sales_project/api.py` নামে নতুন ফাইল তৈরি করো।

> **কেন project folder এ?**  
> Auto-discovery: Bolt project এর `api.py` ও খোঁজে।  
> Auth logic সব app এ common, তাই project-level এ রাখা হয়েছে।

```python
"""
Project-Level API — Authentication Endpoints
=============================================

এই ফাইলের endpoints:
  GET  /api/health         → server alive check (public)
  POST /api/auth/register  → নতুন user তৈরি (public)
  POST /api/auth/login     → JWT token নাও (public)
  GET  /api/auth/me        → নিজের info দেখো (protected)

Public মানে: কোনো login লাগবে না।
Protected মানে: valid JWT token লাগবে।

Global setting (settings.py তে) সব endpoint protected করে।
Public করতে হলে explicitly guards=[AllowAny()] দিতে হয়।
"""

from __future__ import annotations
from typing import Annotated

from django.contrib.auth import aauthenticate  # async authenticate
from django.contrib.auth.models import User
from msgspec import Meta

from django_bolt import BoltAPI
from django_bolt.auth import (
    AllowAny,
    JWTAuthentication,
    IsAuthenticated,
    create_jwt_for_user,   # JWT token তৈরি করার function
)
from django_bolt.exceptions import Unauthorized, BadRequest
from django_bolt.serializers import Serializer, field_validator


# ── BoltAPI Instance ──────────────────────────────────────────────
# prefix="/api" → এই file এর সব route /api/... এর নিচে যাবে
api = BoltAPI(prefix="/api")


# ── Serializers ───────────────────────────────────────────────────

class RegisterInput(Serializer):
    """Registration এর জন্য input validation।"""
    username: Annotated[str, Meta(min_length=3, max_length=150)]
    email: Annotated[str, Meta(pattern=r"^[^@]+@[^@]+\.[^@]+$")]  # basic email regex
    password: Annotated[str, Meta(min_length=8)]
    password_confirm: str

    @field_validator("username")
    def no_spaces_in_username(cls, v: str) -> str:
        if " " in v:
            raise ValueError("Username এ space থাকতে পারবে না।")
        return v.lower()   # lowercase এ store করবো


class LoginInput(Serializer):
    """Login credential।"""
    username: str
    password: str


class TokenResponse(Serializer):
    """Successful login এর JWT token response।"""
    access_token: str
    token_type: str
    expires_in: int
    user_id: int
    username: str


class UserResponse(Serializer):
    """User info response।"""
    id: int
    username: str
    email: str
    is_staff: bool
    is_superuser: bool


# ── Endpoints ──────────────────────────────────────────────────────

@api.get(
    "/health",
    guards=[AllowAny()],   # ← explicitly public করা হয়েছে
    tags=["Health"],
)
async def health_check():
    """
    Server alive কিনা চেক করো।

    guards=[AllowAny()]:
      settings.py এর global IsAuthenticated কে এখানে override করছে।
      এই endpoint এ কোনো token লাগবে না।
    """
    return {"status": "ok", "message": "Sales API চলছে ✓"}


@api.post(
    "/auth/register",
    guards=[AllowAny()],   # public — register করতে token লাগবে না
    tags=["Auth"],
)
async def register(data: RegisterInput) -> UserResponse:
    """
    নতুন user তৈরি করো।

    `data: RegisterInput` কীভাবে কাজ করে?
      Bolt automatically HTTP body parse করে RegisterInput এ convert করে।
      Validation fail হলে 422 Unprocessable Entity return করে।
      Success হলে 'data' object তোমার handler এ আসে।
    """
    # Password match check
    if data.password != data.password_confirm:
        raise BadRequest(detail="Password দুটো মিলছে না।")

    # Duplicate username check — async ORM method
    # aauthenticate, aexists, aget etc. → Django async ORM methods
    if await User.objects.filter(username=data.username).aexists():
        raise BadRequest(detail=f"'{data.username}' username আগে থেকেই নেওয়া।")

    if await User.objects.filter(email=data.email).aexists():
        raise BadRequest(detail="এই email দিয়ে account আগে থেকেই আছে।")

    # User তৈরি করো
    # acreate_user: async + password automatically hash করে (plain text না)
    user = await User.objects.acreate_user(
        username=data.username,
        email=data.email,
        password=data.password,
    )

    # Model থেকে Response Serializer তৈরি করো
    # afrom_model: async version, model এর fields automatically map করে
    return await UserResponse.afrom_model(user)


@api.post(
    "/auth/login",
    guards=[AllowAny()],   # public — login করতে token লাগবে না
    tags=["Auth"],
)
async def login(credentials: LoginInput) -> TokenResponse:
    """
    JWT access token নাও।

    Flow:
    1. username + password দিয়ে authenticate করো
    2. Success হলে JWT token তৈরি করো
    3. Token এ user info + permissions embed করো
    4. Token return করো

    পরবর্তী সব request এ:
    Authorization: Bearer <এই token>
    """

    # Django এর built-in authenticate function (async version)
    # সঠিক credentials হলে User object return করে
    # ভুল হলে None return করে
    user = await aauthenticate(
        username=credentials.username,
        password=credentials.password,
    )

    if user is None:
        raise Unauthorized(detail="Username বা password ভুল।")

    if not user.is_active:
        raise Unauthorized(detail="এই account inactive।")

    # ── JWT Token তৈরি করো ──────────────────────────────────────────
    #
    # গুরুত্বপূর্ণ: Django-Bolt এর guards (IsStaff, HasPermission etc.)
    # Rust এ চলে — database query ছাড়াই।
    # তাই সব permission data টোকেনের ভেতরে embed করতে হয়।
    #
    # create_jwt_for_user automatically include করে:
    #   - user.id  → "sub" claim
    #   - user.is_staff    → "is_staff" claim
    #   - user.is_superuser → "is_superuser" claim
    #   - user.username    → "username" claim
    #   - expiration time  → "exp" claim
    #
    # আমরা extra_claims দিয়ে permissions ও add করছি:
    permissions = list(user.get_all_permissions())
    # get_all_permissions() → ["sales.add_product", "sales.view_order", ...]

    EXPIRE_SECONDS = 60 * 60 * 24  # ২৪ ঘণ্টা

    token = create_jwt_for_user(
        user,
        expires_in=EXPIRE_SECONDS,
        extra_claims={"permissions": permissions},
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=EXPIRE_SECONDS,
        user_id=user.id,
        username=user.username,
    )


@api.get(
    "/auth/me",
    auth=[JWTAuthentication()],   # explicitly JWT চাই
    guards=[IsAuthenticated()],   # explicitly login চাই
    tags=["Auth"],
)
async def get_me(request) -> UserResponse:
    """
    বর্তমান logged-in user এর তথ্য।

    request.user:
      JWT token থেকে user_id বের করে Database থেকে User load করে।
      Lazy loading — শুধু যখন access করো তখনই DB query হয়।
    """
    user = request.user   # DB থেকে user load হবে
    return await UserResponse.afrom_model(user)
```

---

## ১১. ViewSet দিয়ে Product API

এবার `sales/api.py` তৈরি করো:

```bash
# sales/views.py delete করো (bolt এ লাগবে না)
rm sales/views.py

# api.py তৈরি করো
touch sales/api.py
nano sales/api.py
```

```python
"""
Sales App API — Products ও Orders
===================================

Django-Bolt এর ViewSet pattern ব্যবহার করা হয়েছে।

ViewSet vs Function-based view:

Function-based (ছোট project এ ভালো):
  @api.get("/products")
  async def list_products(): ...

  @api.post("/products")
  async def create_product(): ...

  @api.get("/products/{pk}")
  async def get_product(pk: int): ...

ViewSet (বড় project এ ভালো — সব একসাথে organized):
  @api.viewset("/products")
  class ProductViewSet(ViewSet):
      async def list(self, request): ...     # GET /products
      async def create(self, request): ...   # POST /products
      async def retrieve(self, request, pk): # GET /products/{pk}
      async def update(self, request, pk):   # PUT /products/{pk}
      async def destroy(self, request, pk):  # DELETE /products/{pk}
"""

from __future__ import annotations

from django_bolt import BoltAPI, action
from django_bolt.auth import (
    AllowAny,
    IsAuthenticated,
    IsStaff,
    IsAdminUser,
    JWTAuthentication,
)
from django_bolt.exceptions import BadRequest, Forbidden, NotFound
from django_bolt.views import ViewSet

from sales.models import Product, SalesOrder, SalesOrderItem
from sales.serializers import (
    OrderItemResponse,
    ProductCreateInput,
    ProductResponse,
    ProductUpdateInput,
    SalesOrderCreateInput,
    SalesOrderListResponse,
    SalesOrderResponse,
    SalesOrderStatusUpdate,
)

# BoltAPI instance — prefix="/api" মানে সব route /api/ দিয়ে শুরু
api = BoltAPI(prefix="/api")


# ════════════════════════════════════════════════════════════════════
# ██████████████████   PRODUCT VIEWSET   ██████████████████
# ════════════════════════════════════════════════════════════════════

@api.viewset("/products")
class ProductViewSet(ViewSet):
    """
    Product এর CRUD operations।

    @api.viewset("/products") decorator:
      Bolt automatically routes তৈরি করে:
        list()         → GET  /api/products
        create()       → POST /api/products
        retrieve()     → GET  /api/products/{pk}
        update()       → PUT  /api/products/{pk}
        destroy()      → DELETE /api/products/{pk}

    Class-level auth ও guards:
      সব method এ এই auth/guards apply হবে।
      কোনো method এ override করা যায় (action decorator দিয়ে)।
    """

    # Class level এ auth set করা হচ্ছে
    # settings.py তে global আছে, কিন্তু explicit করলে clear থাকে
    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    # ── list: GET /api/products ───────────────────────────────────
    async def list(self, request) -> list[ProductResponse]:
        """
        সব product এর list।

        request.context কী?
          JWT token এ যা embed করা ছিলো তা এখানে পাওয়া যায়।
          DB query ছাড়াই token থেকে is_staff জানা যাচ্ছে।

          context = {
            "user_id": 5,
            "username": "alice",
            "is_staff": True,
            "is_superuser": False,
            "permissions": ["sales.add_product", ...]
          }
        """
        context = request.context
        is_staff = context.get("is_staff", False)

        qs = Product.objects.all()

        # Staff সব দেখবে (active + inactive)
        # Normal user শুধু active দেখবে
        if not is_staff:
            qs = qs.filter(is_active=True)

        results = []
        # async for → async ORM iteration
        # Django 4.1+ এ ORM async support আছে
        async for product in qs:
            results.append(ProductResponse(
                id=product.id,
                name=product.name,
                description=product.description,
                price=float(product.price),   # Decimal → float
                stock_quantity=product.stock_quantity,
                is_active=product.is_active,
            ))

        return results

    # ── create: POST /api/products ────────────────────────────────
    async def create(self, request, data: ProductCreateInput) -> ProductResponse:
        """
        নতুন product তৈরি করো।

        `data: ProductCreateInput`:
          Bolt automatically request body parse করে ProductCreateInput validate করে।
          Valid হলে data object আসে।
          Invalid হলে 422 error যায় (handler call হয় না)।

        Permission check: Staff only
          Guards দিয়েও করা যেতো: @action(guards=[IsStaff()])
          কিন্তু এখানে runtime check করা হয়েছে কারণ:
          - Custom error message দিতে পারছি বাংলায়
          - More flexible control
        """
        context = request.context
        if not context.get("is_staff", False):
            raise Forbidden(detail="শুধুমাত্র Staff user product তৈরি করতে পারবে।")

        # acreate → async version of create()
        product = await Product.objects.acreate(
            name=data.name,
            description=data.description,
            price=data.price,
            stock_quantity=data.stock_quantity,
            is_active=data.is_active,
        )

        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=float(product.price),
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )

    # ── retrieve: GET /api/products/{pk} ──────────────────────────
    async def retrieve(self, request, pk: int) -> ProductResponse:
        """
        একটি product এর detail।

        pk: int → URL এর {pk} part automatically integer এ convert হয়।
        aget() → async get() — একটি object খোঁজে, না পেলে DoesNotExist raise
        """
        try:
            product = await Product.objects.aget(id=pk)
        except Product.DoesNotExist:
            raise NotFound(detail=f"Product #{pk} পাওয়া যায়নি।")

        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=float(product.price),
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )

    # ── update: PUT /api/products/{pk} ────────────────────────────
    async def update(self, request, pk: int, data: ProductUpdateInput) -> ProductResponse:
        """
        Product update করো।

        PUT মানে সাধারণত full replacement।
        কিন্তু আমরা partial update করছি (সুবিধার জন্য)।
        পাঠানো field গুলোই update হবে।
        """
        context = request.context
        if not context.get("is_staff", False):
            raise Forbidden(detail="শুধুমাত্র Staff user product update করতে পারবে।")

        try:
            product = await Product.objects.aget(id=pk)
        except Product.DoesNotExist:
            raise NotFound(detail=f"Product #{pk} পাওয়া যায়নি।")

        # None মানে user সেটা পাঠায়নি → সেই field change করবো না
        if data.name is not None:
            product.name = data.name
        if data.description is not None:
            product.description = data.description
        if data.price is not None:
            product.price = data.price
        if data.stock_quantity is not None:
            product.stock_quantity = data.stock_quantity
        if data.is_active is not None:
            product.is_active = data.is_active

        # asave() → async save — DB তে save করো
        await product.asave()

        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=float(product.price),
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )

    # ── destroy: DELETE /api/products/{pk} ────────────────────────
    async def destroy(self, request, pk: int):
        """
        Product delete করো।

        Permission: Superuser (admin) only।
        IsStaff এর চেয়ে বেশি restriction।
        """
        context = request.context
        if not context.get("is_superuser", False):
            raise Forbidden(detail="শুধুমাত্র Admin (superuser) product delete করতে পারবে।")

        try:
            product = await Product.objects.aget(id=pk)
        except Product.DoesNotExist:
            raise NotFound(detail=f"Product #{pk} পাওয়া যায়নি।")

        # adelete() → async delete
        await product.adelete()
        # None return মানে 204 No Content response
        return None

    # ── Custom Action: GET /api/products/active ───────────────────
    @action(
        methods=["GET"],
        detail=False,      # False = collection action (/products/active)
                           # True  = instance action (/products/{pk}/active)
        path="active",     # URL path: /active
        tags=["Products"],
        summary="শুধু active products দেখো",
    )
    async def active_products(self, request) -> list[ProductResponse]:
        """
        Custom Action: শুধু active products।

        @action decorator দিয়ে extra routes add করা যায়।
        Standard CRUD এর বাইরে যা লাগে।

        detail=False মানে collection action:
          URL: GET /api/products/active
          (কোনো {pk} নেই)

        detail=True মানে instance action:
          URL: POST /api/products/{pk}/publish
          (একটি নির্দিষ্ট product এর action)
        """
        results = []
        async for product in Product.objects.filter(is_active=True):
            results.append(ProductResponse(
                id=product.id,
                name=product.name,
                description=product.description,
                price=float(product.price),
                stock_quantity=product.stock_quantity,
                is_active=product.is_active,
            ))
        return results
```

---

## ১২. ViewSet দিয়ে Sales Order API

`sales/api.py` তে ProductViewSet এর নিচে এই code add করো:

```python

# ════════════════════════════════════════════════════════════════════
# ████████████████   SALES ORDER VIEWSET   ████████████████
# ════════════════════════════════════════════════════════════════════

@api.viewset("/orders")
class SalesOrderViewSet(ViewSet):
    """
    SalesOrder এর CRUD ViewSet।

    Business Logic:
      - যেকোনো authenticated user order তৈরি করতে পারে
      - Normal user শুধু নিজের order দেখতে পারে
      - Staff সব order দেখতে পারে এবং status update করতে পারে
      - Order cancel করলে stock ফেরত যাবে
    """

    auth = [JWTAuthentication()]
    guards = [IsAuthenticated()]

    # ── Helper Method ────────────────────────────────────────────────
    @staticmethod
    async def _build_order_response(order: SalesOrder) -> SalesOrderResponse:
        """
        SalesOrder DB object থেকে SalesOrderResponse তৈরি করো।

        Static method:
          self না থাকলেও call করা যায়।
          ViewSet এর বাইরেও use করা যায়।
          এটা pure utility function।
        """
        from django.contrib.auth.models import User

        # Customer username load
        try:
            customer = await User.objects.aget(id=order.customer_id)
            username = customer.username
        except User.DoesNotExist:
            username = ""

        # Items ও total calculate
        items_data = []
        total = 0.0

        # select_related("product") → JOIN query করে product ও একসাথে load করে
        # এটা না করলে প্রতিটি item এর জন্য আলাদা query হবে (N+1 problem)
        async for item in SalesOrderItem.objects.filter(order=order).select_related("product"):
            line_total = float(item.unit_price) * item.quantity
            total += line_total
            items_data.append(OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product.name,  # select_related এর কারণে extra query নেই
                quantity=item.quantity,
                unit_price=float(item.unit_price),
                line_total=line_total,
            ))

        return SalesOrderResponse(
            id=order.id,
            customer_id=order.customer_id,
            customer_username=username,
            status=order.status,
            customer_note=order.customer_note,
            items=items_data,
            total_amount=total,
        )

    # ── list: GET /api/orders ────────────────────────────────────────
    async def list(self, request) -> list[SalesOrderListResponse]:
        """
        Order list।

        Staff → সব order দেখে
        Normal user → শুধু নিজের order দেখে
        """
        context = request.context
        user_id = context.get("user_id")
        is_staff = context.get("is_staff", False)

        qs = SalesOrder.objects.all()
        if not is_staff:
            qs = qs.filter(customer_id=user_id)

        results = []
        async for order in qs:
            results.append(SalesOrderListResponse(
                id=order.id,
                customer_id=order.customer_id,
                status=order.status,
                total_amount=0.0,       # list এ total skip (performance)
                created_at=str(order.created_at),
            ))
        return results

    # ── create: POST /api/orders ─────────────────────────────────────
    async def create(self, request, data: SalesOrderCreateInput) -> SalesOrderResponse:
        """
        নতুন order তৈরি করো।

        Step by step:
        1. Request validate হয় (Bolt করে)
        2. Products exist ও active কিনা check
        3. Stock enough আছে কিনা check
        4. Order তৈরি করো
        5. Line items তৈরি করো
        6. Stock কমাও
        7. Response return করো
        """
        from django.contrib.auth.models import User

        context = request.context
        user_id = context.get("user_id")

        # Current user load করো
        try:
            customer = await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            raise Forbidden(detail="User পাওয়া যায়নি।")

        # ── Step 1: Products validate ──────────────────────────────────
        product_map: dict[int, Product] = {}
        for item_input in data.items:
            pid = item_input.product_id
            if pid in product_map:
                continue  # একই product দুইবার আসলে একবারই load করবো
            try:
                product = await Product.objects.aget(id=pid, is_active=True)
                product_map[pid] = product
            except Product.DoesNotExist:
                raise BadRequest(
                    detail=f"Product #{pid} পাওয়া যায়নি বা inactive।"
                )

        # ── Step 2: Stock check ────────────────────────────────────────
        # একই product multiple items এ থাকতে পারে, তাই total calculate
        qty_needed: dict[int, int] = {}
        for item_input in data.items:
            pid = item_input.product_id
            qty_needed[pid] = qty_needed.get(pid, 0) + item_input.quantity

        for pid, needed in qty_needed.items():
            product = product_map[pid]
            if product.stock_quantity < needed:
                raise BadRequest(
                    detail=(
                        f"'{product.name}' এর stock কম। "
                        f"চাহিদা: {needed}, মজুদ: {product.stock_quantity}"
                    )
                )

        # ── Step 3: Order তৈরি ────────────────────────────────────────
        order = await SalesOrder.objects.acreate(
            customer=customer,
            customer_note=data.customer_note,
            status="pending",
        )

        # ── Step 4: Line items তৈরি + stock কমাও ─────────────────────
        for item_input in data.items:
            product = product_map[item_input.product_id]

            await SalesOrderItem.objects.acreate(
                order=order,
                product=product,
                quantity=item_input.quantity,
                unit_price=product.price,  # এই মুহূর্তের দাম capture করা হচ্ছে
            )

            # Stock update
            # update_fields=['stock_quantity'] → শুধু এই field DB তে update করো
            # পুরো model save করলে unnecessary columns ও update হবে
            product.stock_quantity -= item_input.quantity
            await product.asave(update_fields=["stock_quantity"])

        return await self._build_order_response(order)

    # ── retrieve: GET /api/orders/{pk} ───────────────────────────────
    async def retrieve(self, request, pk: int) -> SalesOrderResponse:
        """একটি order এর detail।"""
        context = request.context
        user_id = context.get("user_id")
        is_staff = context.get("is_staff", False)

        try:
            order = await SalesOrder.objects.aget(id=pk)
        except SalesOrder.DoesNotExist:
            raise NotFound(detail=f"Order #{pk} পাওয়া যায়নি।")

        # Access control: নিজের order বা staff হতে হবে
        if not is_staff and order.customer_id != user_id:
            raise Forbidden(detail="অন্যের order দেখার permission নেই।")

        return await self._build_order_response(order)

    # ── destroy: DELETE /api/orders/{pk} ─────────────────────────────
    async def destroy(self, request, pk: int):
        """
        Order cancel করো।

        Rules:
        - Normal user → শুধু নিজের 'pending' order cancel করতে পারবে
        - Staff → যেকোনো order delete করতে পারবে
        - Cancel হলে stock ফেরত যাবে
        """
        context = request.context
        user_id = context.get("user_id")
        is_staff = context.get("is_staff", False)

        try:
            order = await SalesOrder.objects.aget(id=pk)
        except SalesOrder.DoesNotExist:
            raise NotFound(detail=f"Order #{pk} পাওয়া যায়নি।")

        # Normal user এর restriction
        if not is_staff:
            if order.customer_id != user_id:
                raise Forbidden(detail="অন্যের order cancel করার permission নেই।")
            if order.status != "pending":
                raise BadRequest(
                    detail=f"'{order.status}' status এর order cancel করা যাবে না।"
                )

        # Stock ফেরত দাও
        async for item in SalesOrderItem.objects.filter(order=order).select_related("product"):
            item.product.stock_quantity += item.quantity
            await item.product.asave(update_fields=["stock_quantity"])

        await order.adelete()
        return None

    # ── Custom Action: POST /api/orders/{pk}/update-status ───────────
    @action(
        methods=["POST"],
        detail=True,         # instance action: /orders/{pk}/update-status
        path="update-status",
        auth=[JWTAuthentication()],
        guards=[IsStaff()],  # ← এই action এ class-level guard override করা হয়েছে
        tags=["Sales Orders"],
        summary="Order status পরিবর্তন (Staff only)",
    )
    async def update_status(
        self,
        request,
        pk: int,
        data: SalesOrderStatusUpdate,
    ) -> SalesOrderResponse:
        """
        Order এর status update করো।

        guards=[IsStaff()] → class এর guards=[IsAuthenticated()] কে
        এই specific action এ override করা হয়েছে।
        শুধু Staff user এই endpoint call করতে পারবে।

        State Machine (কোন status থেকে কোথায় যাওয়া যায়):
          pending   → confirmed, cancelled
          confirmed → shipped,   cancelled
          shipped   → delivered
          delivered → (final — আর change করা যাবে না)
          cancelled → (final — আর change করা যাবে না)
        """
        try:
            order = await SalesOrder.objects.aget(id=pk)
        except SalesOrder.DoesNotExist:
            raise NotFound(detail=f"Order #{pk} পাওয়া যায়নি।")

        # Valid transitions define করো
        valid_transitions = {
            "pending":   ["confirmed", "cancelled"],
            "confirmed": ["shipped", "cancelled"],
            "shipped":   ["delivered"],
            "delivered": [],
            "cancelled": [],
        }

        allowed = valid_transitions.get(order.status, [])
        if data.status not in allowed:
            raise BadRequest(
                detail=(
                    f"'{order.status}' থেকে '{data.status}' তে যাওয়া যায় না। "
                    f"অনুমোদিত: {allowed if allowed else 'কোনোটাই না (final state)'}"
                )
            )

        order.status = data.status
        await order.asave(update_fields=["status"])
        return await self._build_order_response(order)

    # ── Custom Action: GET /api/orders/my-orders ─────────────────────
    @action(
        methods=["GET"],
        detail=False,        # collection action: /orders/my-orders
        path="my-orders",
        tags=["Sales Orders"],
        summary="নিজের সব order দেখো",
    )
    async def my_orders(self, request) -> list[SalesOrderListResponse]:
        """
        Currently logged-in user এর সব order।

        Staff ও যদি এই endpoint call করে, শুধু নিজের order দেখবে।
        (list() এর মতো না — সেখানে staff সব দেখে)
        """
        context = request.context
        user_id = context.get("user_id")

        results = []
        async for order in SalesOrder.objects.filter(customer_id=user_id):
            results.append(SalesOrderListResponse(
                id=order.id,
                customer_id=order.customer_id,
                status=order.status,
                total_amount=0.0,
                created_at=str(order.created_at),
            ))
        return results
```

---

## ১৩. Migration ও Server চালু করা

### Migration কী?

Models তৈরি করলেই database তে table হয় না।  
Migration হলো Python code থেকে SQL তৈরির process।

```
models.py (Python)  →  makemigrations  →  migration files  →  migrate  →  Database tables
```

### Step 1: Migrations তৈরি করো

```bash
# নিশ্চিত করো venv activate আছে এবং sales_project folder এ আছো
python manage.py makemigrations

# Output দেখবে:
# Migrations for 'sales':
#   sales/migrations/0001_initial.py
#     - Create model Product
#     - Create model SalesOrder
#     - Create model SalesOrderItem
```

এই command sales/migrations/0001_initial.py ফাইল তৈরি করবে।  
এটা delete করবে না — version control এ রাখো।

### Step 2: Database তে apply করো

```bash
python manage.py migrate

# Output:
# Operations to perform:
#   Apply all migrations: admin, auth, contenttypes, sales, sessions
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ...
#   Applying sales.0001_initial... OK    ← আমাদেরটা
```

এখন `db.sqlite3` ফাইল তৈরি হবে আমাদের সব table সহ।

### Step 3: Superuser তৈরি করো (Admin Panel ও API test এর জন্য)

```bash
python manage.py createsuperuser

# এরপর জিজ্ঞেস করবে:
# Username: admin
# Email address: admin@example.com
# Password: ********
# Password (again): ********
# Superuser created successfully.
```

### Step 4: Server চালু করো

```bash
python manage.py runbolt --dev

# Output:
# Django-Bolt v0.x.x
# Discovered APIs:
#   sales_project.api (prefix=/api)
#   sales.api (prefix=/api)
# Running on http://127.0.0.1:8000
# API Docs: http://127.0.0.1:8000/docs
```

**`--dev` flag কী করে?**  
- Auto-reload: code change হলে server restart হয়
- Debug mode: বিস্তারিত error দেখায়
- Production এ `--dev` দেবে না

### Swagger UI দেখো:

Browser এ যাও: **http://localhost:8000/docs**

সব endpoint এর interactive documentation দেখবে।  
এখান থেকে directly API test করা যায়।

---

## ১৪. API Test করা (curl দিয়ে)

`curl` হলো command line এ HTTP request করার tool।  
নতুন terminal window খোলো (server চালু রাখো)।

### TOKEN variable set করো (সুবিধার জন্য):

```bash
# এই variable terminal session এ থাকবে
TOKEN=""
STAFF_TOKEN=""
```

### Test 1: Health Check

```bash
curl http://localhost:8000/api/health

# Expected Response:
# {"status":"ok","message":"Sales API চলছে ✓"}
```

### Test 2: User Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "mypass123",
    "password_confirm": "mypass123"
  }'

# Expected Response:
# {"id":1,"username":"alice","email":"alice@example.com","is_staff":false,"is_superuser":false}
```

**curl এর flags:**
- `-X POST` → HTTP POST method use করো
- `-H "Content-Type: application/json"` → body JSON format এ পাঠাচ্ছি বলে জানাও
- `-d '{...}'` → request body (data)

### Test 3: Login (Token নাও)

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "mypass123"}'

# Expected Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "expires_in": 86400,
#   "user_id": 1,
#   "username": "alice"
# }
```

Response থেকে `access_token` copy করো এবং variable এ set করো:

```bash
# Linux/Mac এ automatically token নাও:
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "mypass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: $TOKEN"
```

### Test 4: নিজের Info দেখো (Protected Endpoint)

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected Response:
# {"id":1,"username":"alice","email":"alice@example.com","is_staff":false,"is_superuser":false}
```

**Authorization Header:**
`Authorization: Bearer <token>` এই format এ JWT token পাঠাতে হয়।

### Test 5: Token ছাড়া Protected Endpoint

```bash
curl http://localhost:8000/api/auth/me

# Expected Response (401):
# {"detail": "Authentication required"}
```

### Test 6: Staff Permission দাও এবং Staff Login করো

```bash
# Django shell এ staff permission দাও
python manage.py shell
```

Shell এ:
```python
from django.contrib.auth.models import User
alice = User.objects.get(username='alice')
alice.is_staff = True
alice.save()
print("Done:", alice.is_staff)
exit()
```

এরপর আবার login করো (নতুন token এ is_staff=True থাকবে):

```bash
STAFF_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "mypass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Test 7: Product তৈরি করো (Staff Token দিয়ে)

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ল্যাপটপ Dell XPS 15",
    "description": "উচ্চমানের programming laptop",
    "price": 125000.00,
    "stock_quantity": 10,
    "is_active": true
  }'

# Expected Response:
# {"id":1,"name":"ল্যাপটপ Dell XPS 15","description":"...","price":125000.0,"stock_quantity":10,"is_active":true}
```

আরো কিছু product তৈরি করো:

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Mechanical Keyboard", "price": 8500, "stock_quantity": 25}'

curl -X POST http://localhost:8000/api/products \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "USB-C Monitor 4K", "price": 45000, "stock_quantity": 5}'
```

### Test 8: Products দেখো

```bash
# সব products (staff token দিলে inactive ও দেখায়)
curl http://localhost:8000/api/products \
  -H "Authorization: Bearer $TOKEN"

# একটি product এর detail
curl http://localhost:8000/api/products/1 \
  -H "Authorization: Bearer $TOKEN"

# শুধু active products (custom action)
curl http://localhost:8000/api/products/active \
  -H "Authorization: Bearer $TOKEN"
```

### Test 9: Order তৈরি করো

```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_note": "দ্রুত deliver করুন",
    "items": [
      {"product_id": 1, "quantity": 1},
      {"product_id": 2, "quantity": 2}
    ]
  }'

# Expected Response:
# {
#   "id": 1,
#   "customer_id": 1,
#   "customer_username": "alice",
#   "status": "pending",
#   "customer_note": "দ্রুত deliver করুন",
#   "items": [
#     {"id":1,"product_id":1,"product_name":"ল্যাপটপ...","quantity":1,"unit_price":125000.0,"line_total":125000.0},
#     {"id":2,"product_id":2,"product_name":"Mechanical...","quantity":2,"unit_price":8500.0,"line_total":17000.0}
#   ],
#   "total_amount": 142000.0
# }
```

### Test 10: নিজের Orders দেখো

```bash
curl http://localhost:8000/api/orders/my-orders \
  -H "Authorization: Bearer $TOKEN"
```

### Test 11: Order Status Update (Staff Only)

```bash
curl -X POST http://localhost:8000/api/orders/1/update-status \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

Normal user দিয়ে try করলে:

```bash
curl -X POST http://localhost:8000/api/orders/1/update-status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'

# Expected Response (403):
# {"detail": "Forbidden"}
```

### Test 12: Invalid data পাঠাও (Validation দেখো)

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Authorization: Bearer $STAFF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "", "price": -100}'

# Expected Response (422):
# {
#   "detail": [
#     {"loc":["body","name"],"msg":"Expected `str` of length >= 1","type":"validation_error"},
#     {"loc":["body","price"],"msg":"Expected `float` > 0","type":"validation_error"}
#   ]
# }
```

সব validation error একসাথে দেখায়! (DRF এ প্রথম error দেখায়, পরেরটা fix করলে পরেরটা)

---

## ১৫. সম্পূর্ণ Concept Summary

### Auto-Discovery কীভাবে কাজ করে

```
python manage.py runbolt চালালে:

Django-Bolt →  INSTALLED_APPS দেখে
           →  প্রতিটি app এর api.py খোঁজে
           →  project folder এর api.py ও খোঁজে
           →  সব BoltAPI() instance collect করে
           →  সব routes merge করে একটি router তৈরি করে
           →  Server চালু করে
```

তাই তোমাকে `urls.py` তে কিছু করতে হয় না।

### JWT Authentication Flow

```
Login:
  User → POST /api/auth/login (username + password)
       → Django authenticate() দিয়ে verify
       → create_jwt_for_user() দিয়ে token তৈরি
       → Token এ embed: user_id, is_staff, is_superuser, permissions
       → Token return করো

Protected Request:
  User → GET /api/orders (Authorization: Bearer <token>)
       → Rust layer token validate করে (DB hit নেই!)
       → Token থেকে claims extract করে
       → request.context তে claims রাখে
       → Guard চেক করে (IsAuthenticated, IsStaff, etc.)
       → Handler call করে
       → response return করে
```

### request.context বনাম request.user

```python
# request.context → JWT claims থেকে (DB query ছাড়াই পাওয়া যায়)
context = request.context
user_id = context.get("user_id")     # integer
is_staff = context.get("is_staff")   # boolean
is_admin = context.get("is_superuser")
permissions = context.get("permissions")  # list of strings

# request.user → Database থেকে full User object load করে
user = request.user    # ← এখানে DB query হয়
username = user.username
email = user.email
```

**কখন কোনটা?**
- শুধু `is_staff` check → `request.context` (fast, no DB)
- `user.email` বা অন্য DB field → `request.user` (DB query)

### Guard গুলো

```python
from django_bolt.auth import (
    AllowAny,          # সবাই access করতে পারবে (public endpoint)
    IsAuthenticated,   # Login করা থাকতে হবে (valid JWT)
    IsStaff,           # is_staff=True থাকতে হবে
    IsAdminUser,       # is_superuser=True থাকতে হবে
    HasPermission,     # নির্দিষ্ট Django permission লাগবে
    HasAnyPermission,  # যেকোনো একটা permission হলেই চলবে
    HasAllPermissions, # সব গুলো permission লাগবে
)
```

### @action decorator

```python
@action(
    methods=["GET"],      # HTTP method
    detail=False,         # False=collection, True=instance
    path="custom-path",   # URL path (default: function name)
    auth=[...],           # class-level auth override
    guards=[...],         # class-level guard override
    tags=["MyTag"],       # Swagger UI grouping
    summary="...",        # Short description
)
async def my_action(self, request): ...

# detail=False → GET /api/products/custom-path
# detail=True  → POST /api/products/{pk}/custom-path
```

### Async ORM Methods

```python
# Django 4.1+ এ সব ORM method এর async version আছে:
# 'a' prefix মানে async

# Create
obj = await Model.objects.acreate(field=value)

# Read (একটি)
obj = await Model.objects.aget(id=pk)   # না পেলে DoesNotExist

# Read (অনেক)
async for obj in Model.objects.filter(...):
    ...

# Update
obj.field = new_value
await obj.asave()
await obj.asave(update_fields=["field1", "field2"])  # partial save

# Delete
await obj.adelete()

# Exist check
exists = await Model.objects.filter(...).aexists()
```

### Error Handling

```python
from django_bolt.exceptions import (
    BadRequest,    # 400 — ভুল request (validation fail, business logic error)
    Unauthorized,  # 401 — login নেই বা token invalid
    Forbidden,     # 403 — login আছে কিন্তু permission নেই
    NotFound,      # 404 — resource পাওয়া যায়নি
    HTTPException, # custom status code এর জন্য
)

raise NotFound(detail="Product পাওয়া যায়নি।")
raise Forbidden(detail="তোমার permission নেই।")
raise BadRequest(detail="Price শূন্যের বেশি হতে হবে।")
raise HTTPException(status_code=418, detail="আমি একটি চায়ের কেতলি।")
```

---

## 🎯 Final Project Structure

```
sales_project/
├── manage.py                     ← Django management commands
├── requirements.txt              ← Python dependencies
├── db.sqlite3                    ← SQLite database (auto-generated)
│
├── sales_project/                ← Project configuration
│   ├── __init__.py
│   ├── settings.py               ← Global settings + Bolt auth config
│   ├── asgi.py                   ← ASGI entry point
│   ├── urls.py                   ← Minimal (only admin)
│   └── api.py                    ← Auth endpoints (login, register)
│
└── sales/                        ← Sales feature app
    ├── __init__.py
    ├── models.py                 ← Product, SalesOrder, SalesOrderItem
    ├── serializers.py            ← All input/response serializers
    ├── api.py                    ← ProductViewSet + SalesOrderViewSet
    └── migrations/
        ├── __init__.py
        └── 0001_initial.py       ← Auto-generated migration
```

---

## 🚀 Quick Reference Card

```bash
# ── Project Setup ──────────────────────────────────────────────
mkdir myproject && cd myproject
python -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
django-admin startproject myproject .
python manage.py startapp myapp

# ── Database ───────────────────────────────────────────────────
python manage.py makemigrations    # migration files তৈরি
python manage.py migrate           # database তে apply
python manage.py createsuperuser   # admin user তৈরি

# ── Server ─────────────────────────────────────────────────────
python manage.py runbolt --dev     # development server
# http://localhost:8000/docs        → Swagger UI
# http://localhost:8000/admin       → Django Admin

# ── Django Shell ───────────────────────────────────────────────
python manage.py shell             # interactive Python shell

# ── Testing ────────────────────────────────────────────────────
# Health:  curl http://localhost:8000/api/health
# Login:   curl -X POST .../api/auth/login -H "Content-Type: application/json" -d '{"username":"...","password":"..."}'
# Auth:    curl .../api/... -H "Authorization: Bearer <token>"
```

---

> **Happy Coding! 🎉**  
> প্রশ্ন থাকলে Django-Bolt এর documentation দেখো: https://bolt.farhana.li  
> অথবা GitHub: https://github.com/FarhanAliRaza/django-bolt
