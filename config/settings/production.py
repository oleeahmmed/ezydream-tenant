from .base import *  # noqa: F403, F401

DEBUG = False
# প্রডে প্রতিটি হোস্টের জন্য `Domain` মডেলে রেকর্ড থাকা উচিত; নয়তো ব্যবহারকারী 404 দেখবে।
SHOW_PUBLIC_IF_NO_TENANT_FOUND = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
