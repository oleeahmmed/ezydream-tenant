"""
Tenant auth — ইনপুট ও আউটপুট সিরিয়ালাইজার (``django_bolt_guide.md`` ধারণা)।

``AUTH_USER_MODEL`` = ``apps.auth.models.User`` (ইমেইল লগইন)।
"""

from __future__ import annotations

from django_bolt.serializers import Serializer, field


class RegisterBody(Serializer):
    email: str
    password: str


class LoginBody(Serializer):
    email: str
    password: str


class VerifyLoginOtpBody(Serializer):
    email: str
    otp: str


class RefreshTokenBody(Serializer):
    refresh: str


class ForgotPasswordBody(Serializer):
    email: str | None = field(default=None)


class ResetPasswordBody(Serializer):
    token: str
    new_password: str


class MessageResponse(Serializer):
    detail: str


class LoginTokenResponse(Serializer):
    """Password-only login: tokens. OTP flow: ``otp_required`` + ``detail`` + ``otp_expires_in``."""

    otp_required: bool = field(default=False)
    detail: str = field(default="")
    access: str = field(default="")
    refresh: str = field(default="")
    token_type: str = field(default="Bearer")
    expires_in: int = field(default=0)
    refresh_expires_in: int = field(default=0)
    otp_expires_in: int = field(default=0)


class CurrentUserResponse(Serializer):
    id: int
    email: str
    otp_enabled: bool


class ProfilePatchBody(Serializer):
    otp_enabled: bool
