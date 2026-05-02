# ধাপ ১১ থেকে: ভার্চুয়াল এনভায়রনমেন্ট, চালানো ও PostgreSQL (সম্পূর্ণ গাইড)

এই ফাইল `SETUP_GUIDE_BN.md` এর ধাপ ১০ শেষ করে পড়ুন—এখান থেকে পরের সব বিস্তারিত ও practical ধাপ।

---

## ১১) `django-tenants` দিয়ে এই প্রজেক্টে PostgreSQL কি **`অবশ্যই`** লাগবে?

হ্যাঁ, **বাস্তবে এই স্ট্যাক চালাতে PostgreSQL ব্যতীত উপায় নেই** যেভাবে প্রজেক্টটা গঠিত।

কারণ:

1. লাইব্রেরি নিজের মড্যুল থেকেই **`psycopg2` import** করে (এমনকি ডাটাবেজ SQLite হলেও ডিফল্ট কনফিগে import পর্যন্ত যেতে চায়)—তাই ড্রাইভার লাগবে।
2. `migrate` চালালে ডাটাবেজ wrapper এর **`set_schema`** মেথড লাগে—এটা **PostgreSQL + schema tenancy** এর মতো কাজ করে; SQLite এ এই API থাকে না, তাই `migrate` ব্যর্থ হয়।

**সংক্ষেপ:** স্কিমা-ভিত্তিক multitenant (`django_tenants`) = **PostgreSQL**। ডেভ ও প্রোড দুজায়ই PostgreSQL ব্যবহার করাই সঠিক।

---

## ১২) আপনার মেশিনে PostgreSQL আগেই ইনস্টল আছে—এখন কী করবেন?

নিচের ধাপগুলো sequentially করুন।

### ১২.১ পরিষেবাটা চলছে কিনা চেক করুন

```bash
sudo systemctl status postgresql
```

inactive হলে:

```bash
sudo systemctl start postgresql
```

### ১২.২ ডাটাবেজ ও ব্যবহারকারী তৈরি (recommended)

PostgreSQL এর shell এ ঢুকে (লিনাক্সে সাধারণত):

```bash
sudo -u postgres psql
```

তারপর (নামগুলো ইচ্ছেমতো করতে পারেন; নিচে উদাহরণ):

```sql
CREATE DATABASE ezydream_erp;

CREATE ROLE ezydream_user WITH LOGIN PASSWORD 'এখানে-একটি-জোরালো-পাসওয়ার্ড';

ALTER DATABASE ezydream_erp OWNER TO ezydream_user;

\c ezydream_erp

ALTER SCHEMA public OWNER TO ezydream_user;

GRANT ALL ON SCHEMA public TO ezydream_user;
```

**ডেভ টিপ:** মাল্টিটেন্যান্ট পরে নতুন **schema per tenant** বানাতে চাইলে, ব্যবহারকারীর DB-তে `CREATE`-সংক্রান্ত অনুমতি ঠিক আছে কিনা খেয়াল রাখুন। উপরের টেমপ্লেটে ডেভের জন্য `ezydream_erp`-এ মালিক `ezydream_user` করা হয়েছে।

`\q` চেপে বের হন।

---

## ১৩) Python ভার্চুয়াল এনভায়রনমেন্ট অ্যাক্টিভ করে dependency

প্রজেক্ট root এ:

```bash
cd ezydream-erp-multitanant
source .venv/bin/activate
```

যদি `.venv` না থাকে:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install django django-bolt python-dotenv pillow argon2-cffi django-tenants django-unfold psycopg2-binary
```

`uv` ব্যবহার করলে:

```bash
uv pip install django django-bolt python-dotenv pillow argon2-cffi django-tenants django-unfold psycopg2-binary
```

**ধরে নিন:** `psycopg2-binary` **লাগবে**—PostgreSQL এর জন্য ড্রাইভার।

---

## ১৪) `.env` এ PostgreSQL সংযোগ (এই রিপোর জন্য গুরুত্বপূর্ণ)

এই প্রজেক্টের `config/settings/base.py` এ ডিফল্ট ইঞ্জিন **`django_tenants.postgresql_backend`**—অর্থাৎ `django.db.backends.postgresql` ব্যবহার করবেন না, নইলে `django-tenants` এর schema টুলিং সাথে সাথে কাজ করে না।

উদাহরণ `.env` (ধাপ ১২-এ যে DB/user বানিয়েছেন):

```env
DJANGO_ENV=development
DJANGO_SECRET_KEY=django-insecure-local-dev-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django_tenants.postgresql_backend
DB_NAME=ezydream_erp
DB_USER=ezydream_user
DB_PASSWORD=এখানে-একটি-জোরালো-পাসওয়ার্ড
DB_HOST=127.0.0.1
DB_PORT=5432

TIME_ZONE=Asia/Dhaka
```

**যে কথাগুলো মিস করলেই সাধারণত পড়াপড়ি হয়:**

- ভুল `ENGINE` রাখা (`sqlite` বা শুধু `django.db.backends.postgresql`)  
- ডাটাবেজ create না করা  
- ব্যবহারকারীর schema `public` এর ওপর অনুমতি কম থাকা

---

## ১৫) মাইগ্রেশন ও সার্ভার (হাতে-কলমে)

```bash
source .venv/bin/activate

python manage.py makemigrations
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
python manage.py createsuperuser
python manage.py runserver
```

`django-tenants` এ **শুধু `migrate`** চালালে কখনও কখনও টেন্যান্ট স্কিমাগুলোতে `TENANT_APPS` (যেমন `apps.auth` → `tenant_auth_user`) টেবিল তৈরি হয় না। তাই উপরে **`migrate_schemas --shared`** (পাবলিক/শেয়ার্ড) আর **`migrate_schemas`** (প্রতিটি টেন্যান্ট স্কিমা) দুটোই চালান। নতুন টেন্যান্ট (`create_tenant` ইত্যাদি) বানানোর পরেও **`migrate_schemas`** (বা নির্দিষ্ট স্কিমায় মাইগ্রেট) লাগতে পারে।

`runserver` এখানে ডিফল্টে **Django-Bolt** চালায় (দ্রুত ডেভ সার্ভার)। পুরনো WSGI `runserver` চাইলে: `python manage.py runserver --use-django-runserver`।

### `ProgrammingError: relation "tenant_auth_user" does not exist`

সাধারণত **টেন্যান্ট হোস্ট** (যেমন `acme.localhost`) দিয়ে `/api/auth/register` চালালে কোয়েরি **সেই টেন্যান্টের PostgreSQL স্কিমা** তে যায়। ওই স্কিমায় `tenant_auth` অ্যাপের মাইগ্রেশন এখনো চালানো হয়নি বলে টেবিল নেই। উপরের **`migrate_schemas`** চালিয়ে ঠিক করুন; একটিমাত্র টেন্যান্টের জন্য: `python manage.py migrate_schemas --schema=স্কিমা_নাম`।

### পুরনো `tenant_foundation` (অপসারিত `apps.foundation`)

প্রজেক্ট থেকে **`apps.foundation`** সরানো হয়েছে। পুরনো ডাটাবেজে `tenant_foundation_*` টেবিল বা `django_migrations` এ `tenant_foundation` রেকর্ড থাকলে আর লাগবে না — `psql` দিয়ে প্রয়োজনমতো টেবিল ড্রপ ও `DELETE FROM django_migrations WHERE app = 'tenant_foundation';` (প্রতিটি স্কিমায়) করে পরিষ্কার করতে পারেন। নতুন ইনস্টলে এই ধাপ লাগে না।

### `InconsistentMigrationHistory: admin.0001_initial … tenant_auth.0001_initial_user`

**কারণ:** `public` স্কিমার `django_migrations` এ পুরনো রেকর্ড আছে (যেমন আগে স্টক `User` দিয়ে `admin`/`auth` মাইগ্রেশন চলেছিল)। এখন **`AUTH_USER_MODEL = "tenant_auth.User"`** হওয়ায় Django বলে `admin.0001_initial` এর আগে **`tenant_auth.0001_initial_user`** চালানো দরকার—কিন্তু DB তে সেই ক্রম মানা হয়নি।

**ডেভে (ডাটা ড্রপ করা যায়):** ডাটাবেজ ড্রপ করে আবার তৈরি করো, তারপর উপরের **§১৫** এর সিকোয়েন্স (`migrate_schemas --shared`, `migrate_schemas`, `createsuperuser`)। এক লাইনের উদাহরণ:

```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ezydream_erp;"
sudo -u postgres psql -c "CREATE DATABASE ezydream_erp OWNER ezydream_user;"
```

(`.env` এর `DB_NAME`/`DB_USER` মিলিয়ে নাম বদলাও।)

**প্রোড / ডাটা রাখতে হবে:** Django অফিসিয়াল গাইড + `django-tenants` ডকের মতো ম্যানুয়ালি `django_migrations` ঠিক করা লাগে—একা করো না, ব্যাকআপ নিয়ে।

অ্যাডমিন: `http://127.0.0.1:8000/admin/`

`config/urls.py` এ **`/` → `/admin/`** রিডাইরেক্ট বসানো আছে—তাই সঠিক ডেভ সেটিংসে `http://127.0.0.1:8000/` বা `http://localhost:8000/` খুললে অ্যাডমিনে নিয়ে যাবে (নিচের “No tenant for hostname” এরর ঠিক করা সেটিংস ছাড়া এখনো মিডলওয়্যার 404 দিতে পারে)।

### `Page not found` / **No tenant for hostname "localhost"**

এটা `django_tenants` এর আচরণ।

- Middleware প্রতিটি রিকোয়েস্টে **হোস্টনেম** (যেমন `localhost`, `tenant1.example.com`) দিয়ে **`core_domain`** টেবিলে মিল খুঁজে টেন্যান্ট লোড করে।
- ডাটাবেজে সেই হোস্টের জন্য `Domain` না থাকলে ডিফল্টে **`Http404`** দেখায় টেক্সটে “No tenant for hostname …”।

**এ রিপোতে ডেভের সমাধান (`DJANGO_ENV=development`):**

- `config/settings/development.py` এ **`SHOW_PUBLIC_IF_NO_TENANT_FOUND = True`**
- `config/settings/base.py` এ **`PUBLIC_SCHEMA_URLCONF = "config.urls"`**

এতে হোস্টের জন্য ডাটাবেজে `Domain` না থাকলেও রিকোয়েস্ট **পাবলিক স্কিমা** এর URLconf অনুযায়ী চলে যায় (যেমন অ্যাডমিন)।

**প্রোড (`production.py`):**

- **`SHOW_PUBLIC_IF_NO_TENANT_FOUND = False`** — ডোমেইন ডাটাবেজে না থাকলে 404; এতে সাধারণত প্রতিটি ডোমেইনের জন্য `Client` + `Domain` থাকা উচিত।

ঐচ্ছিক বিকল্প (যেকোনো env): `Domain` টেবিলে `domain='localhost'` লিখে নির্দিষ্ট টেন্যান্ট বাঁধা—তখন `SHOW_PUBLIC` ছাড়াও সেই হোস্টে টেন্যান্ট খুব পরিষ্কার।

### `SHARED_APPS` / `TENANT_APPS` — এক লাইনে সঠিক নিয়ম

`django-tenants` ডকুমেন্টেশন অনুযায়ী **পাবলিক (`public`) স্কিমায় শুধু `SHARED_APPS` সিঙ্ক হয়**, আর **প্রতিটি টেন্যান্ট স্কিমায় শুধু `TENANT_APPS`।

- **`Client` / `Domain` মডেল** (অর্থাৎ `TENANT_MODEL`) যে অ্যাপে আছে সেটা **অবশ্যই `SHARED_APPS`** এ থাকতে হবে। নইলে `public` এর `migrate` টেম রেকর্ড দেখাবে কিন্তু টেবিল তৈরি হবে না—এরপর দ্বিতীয় ধাপে টেন্যান্ট লিস্ট বের করতে গিয়ে `core_client`-টেবিল missing error হয়।

- **`TENANT_APPS` খালি রাখা যাবে না** — এই রিপোতে ডিফল্ট হিসেবে `django.contrib.contenttypes` ব্যবহার করা হয় যাতে প্রতিটি টেন্যান্ট স্কিমাতে সাধারণ ORM মেটাডাটা ও মাইগ্রেশন রুট করা যায়। ব্যবসায়িক মডেল যোগ করলে টেন্যান্ট এক্সক্লুসিভ নতুন অ্যাপ (যেমন `apps.orders`) এখানে যোগ করা হয়।

এই রিপোতে: **`apps.core` → শুধু `SHARED_APPS`** (tenant registry) · **`TENANT_APPS` → অন্তত একটি অ্যাপ (বর্তমানে `contenttypes`)**।

---

## সমস্যা: migrate শেষে `ProgrammingError: relation "core_client" does not exist`

**কখন দেখায়:** পাবলিক স্কিমায় মাইগ্রেশন “OK” মনে হলেও তারপর যখন `migrate_schemas` টেন্যান্টগুলো খুঁজতে `SELECT ... FROM core_client ...` করে।

**কারণ প্রায়ই:** টেন্যান্ট মডেল (`Client`) যে অ্যাপে (`apps/core`) ছিল তা ছিল শুধু `TENANT_APPS`-এ—তাই **রাউটার পাবলিকে সেই টেবিল বানাত না**, কিন্তু `django_migrations` টেবিলে অনেক সময় ট্র্যাকিং খারাপ অবস্থা দেখা দিতে পারে।

### ঠিক করা (কোড আপডেটের পর ডেভ DB recover)

১) আপ টু ডেট কোড নিন (`apps.core` → `SHARED_APPS`; `TENANT_APPS` খালি নয়)।

২) টেমপ্লেট হিসাবে **পাবলিক স্কিমায় টেবিল আছে কিনা চেক**:

```bash
sudo -u postgres psql -d ezydream_erp -c "\\dt public.core_*"
```

কোন `core_client` না থাকলে, ডেভে সবচেয়ে সহজ উপায় ডাটাবেজ ড্রপ করে আব শুরু করা:

```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS ezydream_erp;"
sudo -u postgres psql -c "CREATE DATABASE ezydream_erp OWNER ezydream_user;"
```

৩) এরপর:

```bash
source .venv/bin/activate
python manage.py migrate
```

যদি **ডাটা ড্রপ করা যাবে না**, তখন офিসিয়াল `django-tenants` ডকের “**Moving apps between SHARED_APPS and TENANT_APPS**” ধাপ follow করুন: সেটিংস ঠিক করার পর `django_migrations` থেকে `core`-র ভুল এন্ট্রি সারিয়ে ফের `migrate` / `migrate_schemas --shared`—এগুলো ডেটা ডিপেনডেন্ট, তাই production এ সতর্কতা।

---

## ১৬) আমাদের এই environment এ যা টেস্ট করেছি (আপনার বোঝার জন্য)

1. **`venv`** এ dependency ইনস্টল করার পর **`psycopg2-binary`** যোগ করা হয়—তখনও **SQLite ইঞ্জিন চালালে `migrate`** `set_schema`-সংক্রান্ত error দেয় অর্থাৎ **SQLite multitenant এই সেটআপে ব্যবহারযোগ্য নয়।**  
2. প্রকৃত **`migrate`** সফল করতে হলে উপরের মতো **PostgreSQL + `django_tenants.postgresql_backend` + ওই DB credentials** লাগবে।

আপনার মেশিনে PostgreSQL ঠিকমতো ইউজার ও পাসওয়ার্ড দিয়ে কনফিগ হলেই একই командে `migrate`/`runserver` চলবে।

---

## ১৭) Common errors (PostgreSQL ডেভ ফেজ)

### `django.db.utils.OperationalError: ... connection refused`

- PostgreSQL চালু নয় বা ভুল `DB_HOST`/`DB_PORT`.

### পাসওয়ার্ড চাইছে টার্মিনালে যেন stuck

আগের মতো `psql`-এ **লগইন পদ্ধতি পরিষ্কার** করুন: পাসওয়ার্ড `pg_hba.conf` এর `trust`/`scram`/প্যাসওয়ার্ড মিলিয়ে ঠিক করুন (সিস্টেম ডিফল্টের ওপর নির্ভর করে)।

### `ModuleNotFoundError: No module named 'psycopg2'`

```bash
pip install psycopg2-binary
```

---

## টেন্যান্ট অ্যাডমিন ব্যবহারিক গাইড

- **বাংলা, হাতে-কলমে, দুই ক্লায়েন্ট উদাহরণ:** **`docs/TENANT_CLIENT_ADMIN_GUIDE_BN.md`**
- **ইংরেজি সংক্ষেপ:** **`docs/TENANT_CLIENT_ADMIN_GUIDE.md`**

---

## ১৮) পরবর্তী টেন্যান্ট ডেভ (সংক্ষিপ্ত)

পাবলিক সাইট + টেন্যান্ট-specific URL এর জন্য `PUBLIC_SCHEMA_URLCONF` আলাদা মডিউলে রেখে টেন্যান্টগুলোতে `ROOT_URLCONF` ব্যবহার করা যায়; উপরের সেকশনে `localhost`/ডোমেইন এরর ডেভে কীভাবে ঠেকানো উচিত সেটাই সংক্ষেপ করা হয়েছে।

প্রতিটি টেন্যান্টের জন্য একটি `Client` + প্রযোজ্য `Domain` রেকর্ড (admin বা shell) এরপর সেই ডোমেইন থেকে টেন্যান্ট resolves হয়—সাবডোমেইন/রিসোর্ছ পক্সিসহ বাস্তব সেটাপ আগের ধাপগুলোতে নির্ভর করে।
