# Django-Bolt — সম্পূর্ণ কনফিগারেশন (এই প্রজেক্ট)

এই নথি [Django-Bolt Routing](https://bolt.farhana.li/topics/routing/), [Authentication](https://bolt.farhana.li/topics/authentication/), [Serializers](https://bolt.farhana.li/topics/serializers/), [Class-Based Views](https://bolt.farhana.li/topics/class-based-views/) টপিক গাইডের সাথে সারিবদ্ধ। অফিসিয়াল সাইটে আরও টপিক (Middleware, OpenAPI, Testing ইত্যাদি) আছে।

---

## ১. Django-Bolt কী করে

Django-Bolt Django প্রজেক্টের ভিতরে **উচ্চ থ্রুপুট API** দেয়: রুট ডেকোরেটর (`@api.get`, `@api.post`, …), **ViewSet** / **APIView**, JSON বডি বাইন্ডিং (**msgspec.Struct** বা **Serializer**), এবং [অটো-ডিসকভারি](https://bolt.farhana.li/topics/routing/#auto-discovery) দিয়ে একাধিক `api.py` / অ্যাপ-লেভেল API একসাথে মার্জ হয়।

এই রিপোতে প্রধান এন্ট্রি **`config/api.py`**: এখানে একটি **`BoltAPI`** ইনস্ট্যান্স `api` তৈরি হয়, টেন্যান্ট মিডলওয়্যার ওয়্যার করা হয়, টেন্যান্ট অথ API রুট যুক্ত হয়, শেষে **`mount_django("/", …)`** দিয়ে বাকি সব URL Django ASGI দিয়ে চলে (অ্যাডমিন, স্ট্যাটিক, `urls.py`)।

---

## ২. চালানো

```bash
python manage.py runbolt --dev
```

ডিফল্ট পোর্ট ইত্যাদি `runbolt -h` দেখো। `--dev` অটো-রিলোডের জন্য।

`runbolt` বা এই প্রজেক্টের ডিফল্ট **`runserver`** (যেটা Bolt চালায়) দিয়ে **`/api/auth/...`** পাওয়া যায়। **`runserver --use-django-runserver`** (ক্লাসিক Django) চালালে Bolt রুট থাকে না — তখন অথ API থাকবে না (`config/urls.py` এ `/api/auth/` ইনক্লুড নেই)।

---

## ৩. অটো-ডিসকভারি ও `config.api`

[Routing — Auto-discovery](https://bolt.farhana.li/topics/routing/#auto-discovery) অনুযায়ী Bolt `BoltAPI()` অ্যাসাইনমেন্ট খোঁজে:

1. প্রজেক্ট প্যাকেজে — `ROOT_URLCONF` যেমন `config.urls` হলে **`config.api`** ও **`config.bolt_api`** ক্যান্ডিডেট।
2. প্রতিটি ইনস্টলড অ্যাপে — **`{app}.api`** (যেমন `apps.auth.api`)।

এই প্রজেক্টে **রুট এক জায়গায়** রাখা হয়েছে: **`config/api.py`** এ `api = BoltAPI(...)` এবং `attach_auth_routes(api)`। অ্যাপে আলাদা `BoltAPI()` তৈরি করা হয় না (`apps/auth/api/` শুধু রুট রেজিস্টার + ভিউ) — ডুপ্লিকেট মাউন্ট এড়াতে।

---

## ৪. ট্রেইলিং স্ল্যাশ

[Trailing slash handling](https://bolt.farhana.li/topics/routing/#trailing-slash-handling): ডিফল্ট **`strip`** — রেজিস্ট্রেশনের সময় `/path/` → `/path`। ক্যাননিকাল URL না হলে **৩০৮** রিডাইরেক্ট হতে পারে।

`urlpatterns` এ Django ঐতিহ্যগতভাবে `register/` রাখলে শুধু ক্লাসিক `runserver` এর কথা ভাবলে প্রযোজ্য; Bolt পথ **`/api/auth/register`** (ট্রেইলিং স্ল্যাশ `strip` নিয়ম)।

---

## ৫. এই রিপোতে রুট কীভাবে লেখা

[Class-Based Views](https://bolt.farhana.li/topics/class-based-views/) — এই প্রজেক্টে **`apps/auth/api/views.py`** এক ফাইলেই `Serializer`, `APIView` ক্লাস, `attach_auth_routes(api)` (`api.view(path)(ViewClass)`), আর **`apps/auth/api/__init__.py`** শুধু `attach_auth_routes` এক্সপোর্ট করে।

চাইলে পরে [ViewSet](https://bolt.farhana.li/topics/class-based-views/) দিয়ে গ্রুপ করা যায় — বড় অ্যাপে সুবিধা।

---

## ৬. রিকোয়েস্ট বডি

এখন বডি **`django_bolt.serializers.Serializer`** দিয়ে ভ্যালিডেট (`RegisterIn`, …) — `apps/auth/api/views.py`।

---

## ৭. Django মিডলওয়্যার (টেন্যান্ট)

`BoltAPI` তে **`DjangoMiddleware(TenantMainMiddleware)`** — প্রতিটি Bolt রিকোয়েস্টে django-tenants যেন **`search_path`** ঠিকমতো সেট করে। পূর্ণ django-tenants সেটআপ: **`docs/DJANGO_TENANTS_SETUP_BN.md`**।

---

## ৮. `mount_django`

[ASGI mounts](https://bolt.farhana.li/topics/routing/#asgi-mounts) ধারণা: Bolt যে পথ ম্যাচ করে না, সেখানে Django ASGI (অ্যাডমিন, ইত্যাদি)। আমরা **`/`** এ মাউন্ট করেছি (`clear_root_path=True`) যাতে Django URL পাথ ঠিক থাকে।

---

## ৯. JWT ও Authentication টপিক

[Bolt JWTAuthentication](https://bolt.farhana.li/topics/authentication/#jwt-authentication) ডিফল্টভাবে **`django.contrib.auth.User`** লোড করার ধারণার উপর (`sub` = ইউজার pk)।

এই প্রজেক্টের **টেন্যান্ট ইউজার** টোকেন **`django_bolt.auth.Token`** দিয়ে তৈরি। **`/api/auth/me`** এ **`JWTAuthentication` + `IsAuthenticated()`** — `sub` দিয়ে **`AUTH_USER_MODEL`** (`tenant_auth.User`) লোড হয়, হ্যান্ডলার **`request.user`** থেকে `id`/`email` দেয়।

গ্লোবাল **`BOLT_AUTHENTICATION_CLASSES`** / **`BOLT_DEFAULT_PERMISSION_CLASSES`** সেট করলে সব রুট প্রভাবিত হবে — প্রোডাকশনে সচেতনভাবে কনফিগার করো ([Global authentication](https://bolt.farhana.li/topics/authentication/#global-authentication))।

---

## ১০. ফাইল মানচিত্র (সংক্ষেপ)

| ফাইল | ভূমিকা |
|------|--------|
| `config/api.py` | `BoltAPI`, মিডলওয়্যার, `mount_django`, `attach_auth_routes(api)` |
| `apps/auth/api/` | এক `views.py`: Bolt `APIView` + `attach_auth_routes` |
| `apps/auth/views.py` | খালি (শুধু Bolt API) |

---

**সংক্ষেপ:** `runbolt` + `config/api.py` + ছোট `@api.post`/`get` হ্যান্ডলার + `DjangoMiddleware(TenantMainMiddleware)` + `mount_django` — শুরু করার জন্য সরল বিন্যাস; প্রয়োজনে পরে ViewSet/Serializer যোগ।
