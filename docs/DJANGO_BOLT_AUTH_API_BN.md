# টেন্যান্ট অথ API — Django-Bolt

এই নথি **ইমেইল-লগইন ইউজার (`tenant_auth.User`)** রেজিস্টার/লগইন/পাসওয়ার্ড রিসেট ও **`/me`** বর্ণনা করে। রাউট [Class-Based Views](https://bolt.farhana.li/topics/class-based-views/) (`APIView` + `api.view(...)`) — কোড **`apps/auth/api/views.py`** (এক ফাইল)। JWT ধারণা [Authentication](https://bolt.farhana.li/topics/authentication/) টপিকের সাথে মিলিয়ে পড়লে উপকার।

**টেন্যান্ট স্কিমা:** রিকোয়েস্টের **`Host`** অবশ্যই সেই টেন্যান্টের ডোমেইন হতে হবে (যেমন `acme.localhost`) — বিস্তারিত **`docs/DJANGO_TENANTS_SETUP_BN.md`**।

---

## ১. এন্ডপয়েন্ট তালিকা

| মেথড | Bolt পথ (`strip` স্ল্যাশ) |
|--------|---------------------------|
| POST | `/api/auth/register` |
| POST | `/api/auth/login` |
| POST | `/api/auth/forgot-password` |
| POST | `/api/auth/reset-password` |
| GET | `/api/auth/me` |

`runbolt` এ ৩০৮ রিডাইরেক্ট হলে ব্রাউজার/ক্লায়েন্ট **ক্যাননিকাল** URL অনুসরণ করবে।

---

## ২. রিকোয়েস্ট বডি (JSON)

### POST `/api/auth/register`

```json
{ "email": "user@example.com", "password": "minimum8chars" }
```

**২০১:** `{ "detail": "registered" }`  
**৪০০:** ডুপ্লিকেট ইমেইল / ইনভ্যালিড ইমেইল / ছোট পাসওয়ার্ড।

### POST `/api/auth/login`

```json
{ "email": "user@example.com", "password": "…" }
```

**২০০:** `{ "access": "<JWT>", "token_type": "Bearer", "expires_in": <সেকেন্ড> }`  
**৪০১:** ভুল ইমেইল/পাসওয়ার্ড।

টোকেন **`django_bolt.auth.Token`** দিয়ে সাইন, ক্লেইমে **`sub`**: `User` এর pk, **`email`**। `JWTAuthentication` একই `AUTH_USER_MODEL` ইউজার লোড করে।

### POST `/api/auth/forgot-password`

```json
{}
```

বা

```json
{ "email": "user@example.com" }
```

সবসময় একই সাফল্য বার্তা (ইমেইল এনামারেশন এড়াতে)। সার্ভার লগে রিসেট টোকেন দেখা যাবে (ডেভ)।

### POST `/api/auth/reset-password`

```json
{ "token": "<urlsafe_token>", "new_password": "minimum8chars" }
```

### GET `/api/auth/me`

হেডার:

```http
Authorization: Bearer <login থেকে পাওয়া access টোকেন>
```

**২০০:** `{ "id": <int>, "email": "<str>" }`  
**৪০১:** টোকেন নেই / ভুল / টাইপ ভুল / ইউজার নেই।

> **নোট:** `JWTAuthentication` + `IsAuthenticated()` JWT যাচাই করে `request.user` সেট করে; **`/me`** শুধু `id` ও `email` ফেরত দেয়।

---

## ৩. `curl` উদাহরণ (টেন্যান্ট হোস্ট)

```bash
curl -sS -X POST "http://acme.localhost:8000/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"email":"u@example.com","password":"secret1234"}'

curl -sS -X POST "http://acme.localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"u@example.com","password":"secret1234"}'

# TOKEN=... পূরণ করো
curl -sS "http://acme.localhost:8000/api/auth/me/" \
  -H "Authorization: Bearer $TOKEN"
```

`runbolt` চালালে URL হোস্ট/পোর্ট ব্যানার অনুযায়ী; পথ একই লজিক (`/api/auth/...`)।

---

## ৪. কোড কোথায়

| অংশ | ফাইল |
|------|------|
| কোড | `apps/auth/api/views.py` (Bolt); `apps/auth/urls.py` খালি |
| Bolt রুট মাউন্ট | `config/api.py` |

---

## ৫. সেটিংস (সময় ও রিসেট)

`config/settings/base.py`:

- **`AUTH_ACCESS_TOKEN_SECONDS`** — JWT মেয়াদ (ডিফল্ট ৩৬০০)।
- **`AUTH_PASSWORD_RESET_HOURS`** — রিসেট টোকেন বৈধতা (ডিফল্ট ২৪ ঘণ্টা)।

---

**সংক্ষেপ:** টেন্যান্ট হোস্ট + JSON বডি + লগইনে JWT + **`/me`** তে `Authorization: Bearer` — Bolt ও Django উভয় রানটাইমে একই `service` লেয়ার।
