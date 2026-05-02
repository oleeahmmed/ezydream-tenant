from .base import *  # noqa: F403, F401

DEBUG = True
# localhost টেন্যান্ট ডোমেইন ডাটাবেজে না থাকলে পাবলিক স্কিমা + PUBLIC_SCHEMA_URLCONF ব্যবহার হবে
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True
