from __future__ import annotations

from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class EmailUserManager(BaseUserManager):
    """ইমেইল = লগইন আইডি (``USERNAME_FIELD``)।"""

    def create_user(self, email: str, password: str | None = None, **extra):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra)


class AbstractTenantEmailUser(AbstractBaseUser, PermissionsMixin):
    """টেন্যান্ট-স্কোপড ইমেইল-লগইন ইউজারের অ্যাবস্ট্রাক্ট বেস।"""

    username = None
    email = models.EmailField("email address", unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=128, blank=True, default="", db_index=True)
    reset_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    objects = EmailUserManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class User(AbstractTenantEmailUser):
    """প্রতি টেন্যান্ট স্কিমায় আলাদা সারি (``SHARED_APPS`` + ``TENANT_APPS`` এ ``apps.auth``)।"""

    otp_enabled = models.BooleanField(
        default=False,
        help_text="If True, email OTP is required after password check on login.",
    )
    login_otp_hash = models.CharField(max_length=200, blank=True, default="")
    login_otp_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self) -> str:
        return self.email
